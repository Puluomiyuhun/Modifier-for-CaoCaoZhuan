"""Type-safe process memory access and transactional patching."""

from __future__ import annotations

import ctypes
import os
import struct
from contextlib import contextmanager
from ctypes import wintypes
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from engine_profile import (DynamicPatchSpec, PatchSpec,
                            REFERENCE_IMAGE_BASE)


PROCESS_CREATE_THREAD = 0x0002
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
SYNCHRONIZE = 0x00100000

MEM_COMMIT = 0x1000
MEM_RELEASE = 0x8000
PAGE_NOACCESS = 0x01
PAGE_GUARD = 0x100
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08
PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
TH32CS_SNAPTHREAD = 0x00000004
THREAD_SUSPEND_RESUME = 0x0002
THREAD_GET_CONTEXT = 0x0008
THREAD_QUERY_INFORMATION = 0x0040
CONTEXT_i386 = 0x00010000
CONTEXT_CONTROL = CONTEXT_i386 | 0x00000001

READABLE_PROTECTIONS = {
    PAGE_READONLY, PAGE_READWRITE, PAGE_WRITECOPY, PAGE_EXECUTE,
    PAGE_EXECUTE_READ, PAGE_EXECUTE_READWRITE, PAGE_EXECUTE_WRITECOPY,
}
WRITABLE_PROTECTIONS = {
    PAGE_READWRITE, PAGE_WRITECOPY, PAGE_EXECUTE_READWRITE,
    PAGE_EXECUTE_WRITECOPY,
}


class MemoryAccessError(RuntimeError):
    pass


class PatchError(MemoryAccessError):
    pass


class _MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


class _MODULEENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("th32ModuleID", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("GlblcntUsage", wintypes.DWORD),
        ("ProccntUsage", wintypes.DWORD),
        ("modBaseAddr", ctypes.POINTER(ctypes.c_byte)),
        ("modBaseSize", wintypes.DWORD),
        ("hModule", wintypes.HMODULE),
        ("szModule", wintypes.WCHAR * 256),
        ("szExePath", wintypes.WCHAR * 260),
    ]


class _THREADENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ThreadID", wintypes.DWORD),
        ("th32OwnerProcessID", wintypes.DWORD),
        ("tpBasePri", wintypes.LONG),
        ("tpDeltaPri", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
    ]


class _FLOATING_SAVE_AREA(ctypes.Structure):
    _fields_ = [
        ("ControlWord", wintypes.DWORD), ("StatusWord", wintypes.DWORD),
        ("TagWord", wintypes.DWORD), ("ErrorOffset", wintypes.DWORD),
        ("ErrorSelector", wintypes.DWORD), ("DataOffset", wintypes.DWORD),
        ("DataSelector", wintypes.DWORD), ("RegisterArea", ctypes.c_byte * 80),
        ("Cr0NpxState", wintypes.DWORD),
    ]


class _CONTEXT32(ctypes.Structure):
    _fields_ = [
        ("ContextFlags", wintypes.DWORD),
        ("Dr0", wintypes.DWORD), ("Dr1", wintypes.DWORD),
        ("Dr2", wintypes.DWORD), ("Dr3", wintypes.DWORD),
        ("Dr6", wintypes.DWORD), ("Dr7", wintypes.DWORD),
        ("FloatSave", _FLOATING_SAVE_AREA),
        ("SegGs", wintypes.DWORD), ("SegFs", wintypes.DWORD),
        ("SegEs", wintypes.DWORD), ("SegDs", wintypes.DWORD),
        ("Edi", wintypes.DWORD), ("Esi", wintypes.DWORD),
        ("Ebx", wintypes.DWORD), ("Edx", wintypes.DWORD),
        ("Ecx", wintypes.DWORD), ("Eax", wintypes.DWORD),
        ("Ebp", wintypes.DWORD), ("Eip", wintypes.DWORD),
        ("SegCs", wintypes.DWORD), ("EFlags", wintypes.DWORD),
        ("Esp", wintypes.DWORD), ("SegSs", wintypes.DWORD),
        ("ExtendedRegisters", ctypes.c_byte * 512),
    ]


@contextmanager
def suspended_thread_eips(pid: int):
    """Suspend all target threads and yield their x86 instruction pointers."""
    if os.name != "nt":
        raise MemoryAccessError("动态 stub 线程检查只支持 Windows")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    wow64 = ctypes.sizeof(ctypes.c_void_p) == 8
    kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel32.Thread32First.argtypes = [wintypes.HANDLE, ctypes.POINTER(_THREADENTRY32)]
    kernel32.Thread32First.restype = wintypes.BOOL
    kernel32.Thread32Next.argtypes = [wintypes.HANDLE, ctypes.POINTER(_THREADENTRY32)]
    kernel32.Thread32Next.restype = wintypes.BOOL
    kernel32.OpenThread.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenThread.restype = wintypes.HANDLE
    kernel32.SuspendThread.argtypes = [wintypes.HANDLE]
    kernel32.SuspendThread.restype = wintypes.DWORD
    kernel32.ResumeThread.argtypes = [wintypes.HANDLE]
    kernel32.ResumeThread.restype = wintypes.DWORD
    context_api = (kernel32.Wow64GetThreadContext if wow64
                   else kernel32.GetThreadContext)
    context_api.argtypes = [wintypes.HANDLE, ctypes.POINTER(_CONTEXT32)]
    context_api.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if snapshot in (0, -1, ctypes.c_void_p(-1).value):
        raise MemoryAccessError("枚举目标线程失败")
    suspended = []
    eips = []
    try:
        entry = _THREADENTRY32()
        entry.dwSize = ctypes.sizeof(entry)
        ok = kernel32.Thread32First(snapshot, ctypes.byref(entry))
        while ok:
            if int(entry.th32OwnerProcessID) == int(pid):
                access = (THREAD_SUSPEND_RESUME | THREAD_GET_CONTEXT |
                          THREAD_QUERY_INFORMATION)
                handle = kernel32.OpenThread(access, False, entry.th32ThreadID)
                if not handle:
                    raise MemoryAccessError("打开目标线程失败")
                if kernel32.SuspendThread(handle) == 0xFFFFFFFF:
                    kernel32.CloseHandle(handle)
                    raise MemoryAccessError("暂停目标线程失败")
                suspended.append(handle)
                context = _CONTEXT32()
                context.ContextFlags = CONTEXT_CONTROL
                if not context_api(handle, ctypes.byref(context)):
                    raise MemoryAccessError("读取目标线程 EIP 失败")
                eips.append(int(context.Eip))
            ok = kernel32.Thread32Next(snapshot, ctypes.byref(entry))
        yield tuple(eips)
    finally:
        for handle in reversed(suspended):
            kernel32.ResumeThread(handle)
            kernel32.CloseHandle(handle)
        kernel32.CloseHandle(snapshot)


def get_process_module(pid: int, module_name: str = "Ekd5.exe") -> Tuple[int, int, str]:
    """Return actual module base, image size and path for a 32-bit process."""
    if os.name != "nt":
        raise MemoryAccessError("模块枚举只支持 Windows")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel32.Module32FirstW.argtypes = [wintypes.HANDLE,
                                        ctypes.POINTER(_MODULEENTRY32W)]
    kernel32.Module32FirstW.restype = wintypes.BOOL
    kernel32.Module32NextW.argtypes = [wintypes.HANDLE,
                                       ctypes.POINTER(_MODULEENTRY32W)]
    kernel32.Module32NextW.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000008 | 0x00000010, int(pid))
    if snapshot in (0, -1, ctypes.c_void_p(-1).value):
        raise MemoryAccessError("枚举游戏模块失败，WinError=%d" % ctypes.get_last_error())
    try:
        entry = _MODULEENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        ok = kernel32.Module32FirstW(snapshot, ctypes.byref(entry))
        while ok:
            if entry.szModule.lower() == module_name.lower():
                return (ctypes.cast(entry.modBaseAddr, ctypes.c_void_p).value or 0,
                        int(entry.modBaseSize), entry.szExePath)
            ok = kernel32.Module32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(snapshot)
    raise MemoryAccessError("目标进程中没有找到 %s 模块" % module_name)


class Win32Backend:
    def __init__(self, handle: int):
        if os.name != "nt":
            raise MemoryAccessError("进程内存调试只支持 Windows")
        self.handle = int(handle)
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._declare_api()

    def _declare_api(self) -> None:
        k32 = self.kernel32
        k32.ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                          ctypes.c_void_p, ctypes.c_size_t,
                                          ctypes.POINTER(ctypes.c_size_t)]
        k32.ReadProcessMemory.restype = wintypes.BOOL
        k32.WriteProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                           ctypes.c_void_p, ctypes.c_size_t,
                                           ctypes.POINTER(ctypes.c_size_t)]
        k32.WriteProcessMemory.restype = wintypes.BOOL
        k32.FlushInstructionCache.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                               ctypes.c_size_t]
        k32.FlushInstructionCache.restype = wintypes.BOOL
        k32.VirtualQueryEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                       ctypes.POINTER(_MEMORY_BASIC_INFORMATION),
                                       ctypes.c_size_t]
        k32.VirtualQueryEx.restype = ctypes.c_size_t
        k32.VirtualProtectEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                         ctypes.c_size_t, wintypes.DWORD,
                                         ctypes.POINTER(wintypes.DWORD)]
        k32.VirtualProtectEx.restype = wintypes.BOOL
        k32.VirtualAllocEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                       ctypes.c_size_t, wintypes.DWORD,
                                       wintypes.DWORD]
        k32.VirtualAllocEx.restype = ctypes.c_void_p
        k32.VirtualFreeEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                      ctypes.c_size_t, wintypes.DWORD]
        k32.VirtualFreeEx.restype = wintypes.BOOL
        k32.CreateRemoteThread.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                           ctypes.c_size_t, ctypes.c_void_p,
                                           ctypes.c_void_p, wintypes.DWORD,
                                           ctypes.POINTER(wintypes.DWORD)]
        k32.CreateRemoteThread.restype = wintypes.HANDLE
        k32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        k32.WaitForSingleObject.restype = wintypes.DWORD
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
        k32.CloseHandle.restype = wintypes.BOOL

    def read(self, address: int, size: int) -> bytes:
        buffer = ctypes.create_string_buffer(size)
        transferred = ctypes.c_size_t(0)
        ok = self.kernel32.ReadProcessMemory(
            self.handle, ctypes.c_void_p(address), buffer, size,
            ctypes.byref(transferred))
        if not ok or transferred.value != size:
            raise MemoryAccessError(
                "读取 0x%08X 失败，实际 %d/%d 字节，WinError=%d" %
                (address, transferred.value, size, ctypes.get_last_error()))
        return buffer.raw

    def write(self, address: int, data: bytes) -> int:
        transferred = ctypes.c_size_t(0)
        buffer = ctypes.create_string_buffer(data, len(data))
        ok = self.kernel32.WriteProcessMemory(
            self.handle, ctypes.c_void_p(address), buffer, len(data),
            ctypes.byref(transferred))
        if not ok:
            raise MemoryAccessError(
                "写入 0x%08X 失败，WinError=%d" %
                (address, ctypes.get_last_error()))
        self.flush(address, len(data))
        return int(transferred.value)

    def flush(self, address: int, size: int) -> None:
        if not self.kernel32.FlushInstructionCache(
                self.handle, ctypes.c_void_p(address), size):
            raise MemoryAccessError("刷新指令缓存失败，WinError=%d" %
                                    ctypes.get_last_error())

    def query(self, address: int) -> Tuple[int, int, int, int]:
        info = _MEMORY_BASIC_INFORMATION()
        result = self.kernel32.VirtualQueryEx(
            self.handle, ctypes.c_void_p(address), ctypes.byref(info),
            ctypes.sizeof(info))
        if not result:
            raise MemoryAccessError("查询内存页 0x%08X 失败" % address)
        return int(info.BaseAddress or 0), int(info.RegionSize), int(info.State), int(info.Protect)

    def protect(self, address: int, size: int, protection: int) -> int:
        old = wintypes.DWORD(0)
        if not self.kernel32.VirtualProtectEx(
                self.handle, ctypes.c_void_p(address), size, protection,
                ctypes.byref(old)):
            raise MemoryAccessError("修改内存页保护失败，WinError=%d" % ctypes.get_last_error())
        return int(old.value)

    def allocate(self, size: int, protection: int = PAGE_READWRITE) -> int:
        address = self.kernel32.VirtualAllocEx(
            self.handle, None, size, 0x1000 | 0x2000, protection)
        if not address:
            raise MemoryAccessError("分配远程内存失败，WinError=%d" % ctypes.get_last_error())
        return int(address)

    def free(self, address: int) -> None:
        if address and not self.kernel32.VirtualFreeEx(
                self.handle, ctypes.c_void_p(address), 0, MEM_RELEASE):
            raise MemoryAccessError("释放远程内存失败，WinError=%d" % ctypes.get_last_error())

    def create_thread(self, start: int, parameter: int) -> int:
        thread_id = wintypes.DWORD(0)
        handle = self.kernel32.CreateRemoteThread(
            self.handle, None, 0, ctypes.c_void_p(start),
            ctypes.c_void_p(parameter), 0, ctypes.byref(thread_id))
        if not handle:
            raise MemoryAccessError("创建远程线程失败，WinError=%d" % ctypes.get_last_error())
        return int(handle)

    def wait_thread(self, thread: int, timeout_ms: int) -> None:
        result = self.kernel32.WaitForSingleObject(thread, timeout_ms)
        if result == 0x00000102:
            raise MemoryAccessError("远程线程执行超时")
        if result != 0:
            raise MemoryAccessError("等待远程线程失败，返回值=0x%08X" % result)

    def close_thread(self, thread: int) -> None:
        if thread:
            self.kernel32.CloseHandle(thread)

    def close(self) -> None:
        if self.handle:
            self.kernel32.CloseHandle(self.handle)
            self.handle = 0


@dataclass(frozen=True)
class DynamicPatchLease:
    spec: DynamicPatchSpec
    allocation: int
    allocation_size: int
    branch_bytes: Tuple[bytes, ...]


class MemorySession:
    """A process session compatible with old Read/WriteProcessMemory calls."""

    def __init__(self, handle: int, module_base: int, module_size: int,
                 backend=None, owns_handle: bool = True,
                 reference_image_base: int = REFERENCE_IMAGE_BASE,
                 pid: Optional[int] = None):
        self.handle = int(handle)
        self.pid = pid
        self.module_base = int(module_base)
        self.module_size = int(module_size)
        self.reference_image_base = int(reference_image_base)
        self.backend = backend if backend is not None else Win32Backend(handle)
        self.owns_handle = owns_handle
        self.closed = False
        self.last_error = ""
        self.error_handler = None
        self._active_patches: Dict[str, PatchSpec] = {}
        self._dynamic_leases: Dict[str, DynamicPatchLease] = {}
        self._orphaned_allocations = []

    @classmethod
    def open_pid(cls, pid: int, module_base: int, module_size: int,
                 reference_image_base: int = REFERENCE_IMAGE_BASE) -> "MemorySession":
        if os.name != "nt":
            raise MemoryAccessError("进程内存调试只支持 Windows")
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        access = (PROCESS_QUERY_INFORMATION | PROCESS_VM_OPERATION |
                  PROCESS_VM_READ | PROCESS_VM_WRITE | SYNCHRONIZE)
        handle = kernel32.OpenProcess(access, False, int(pid))
        if not handle:
            raise MemoryAccessError("打开游戏进程失败，WinError=%d" % ctypes.get_last_error())
        return cls(int(handle), module_base, module_size, owns_handle=True, pid=pid,
                   reference_image_base=reference_image_base)

    def resolve_reference(self, address: int) -> int:
        upper = self.reference_image_base + self.module_size
        if self.reference_image_base <= address < upper:
            return self.module_base + address - self.reference_image_base
        return address

    def validate_range(self, address: int, size: int, write: bool = False) -> bool:
        if self.closed or address <= 0 or size <= 0:
            return False
        address = self.resolve_reference(address)
        return self.validate_actual_range(address, size, write)

    def validate_actual_range(self, address: int, size: int,
                              write: bool = False) -> bool:
        if self.closed or address <= 0 or size <= 0:
            return False
        end = address + size
        cursor = address
        try:
            while cursor < end:
                base, region_size, state, protection = self.backend.query(cursor)
                if state != MEM_COMMIT or protection & (PAGE_NOACCESS | PAGE_GUARD):
                    return False
                normalized = protection & 0xFF
                allowed = WRITABLE_PROTECTIONS if write else READABLE_PROTECTIONS
                if normalized not in allowed:
                    return False
                region_end = base + region_size
                if region_end <= cursor:
                    return False
                cursor = min(region_end, end)
            return True
        except MemoryAccessError:
            return False

    def _check_open(self) -> None:
        if self.closed:
            raise MemoryAccessError("游戏进程会话已关闭")

    def read_bytes(self, address: int, size: int) -> bytes:
        self._check_open()
        actual = self.resolve_reference(address)
        if not self.validate_actual_range(actual, size, write=False):
            raise MemoryAccessError("拒绝读取无效或不可读范围 0x%08X+0x%X" % (actual, size))
        return self.backend.read(actual, size)

    def read_actual_bytes(self, address: int, size: int) -> bytes:
        self._check_open()
        if not self.validate_actual_range(address, size, write=False):
            raise MemoryAccessError("拒绝读取无效运行时范围 0x%08X+0x%X" %
                                    (address, size))
        return self.backend.read(address, size)

    def read_many(self, address: int, size: int) -> bytes:
        return self.read_bytes(address, size)

    def read_u8(self, address: int) -> int:
        return self.read_bytes(address, 1)[0]

    def read_u16(self, address: int) -> int:
        return struct.unpack("<H", self.read_bytes(address, 2))[0]

    def read_u32(self, address: int) -> int:
        return struct.unpack("<I", self.read_bytes(address, 4))[0]

    def write_bytes(self, address: int, data: bytes, verify: bool = True,
                    allow_protect: bool = False) -> None:
        self._check_open()
        if not isinstance(data, bytes) or not data:
            raise MemoryAccessError("写入数据必须是非空 bytes")
        actual = self.resolve_reference(address)
        restore_protection: Optional[int] = None
        if not self.validate_actual_range(actual, len(data), write=True):
            if not allow_protect or not self.validate_actual_range(actual, len(data), write=False):
                raise MemoryAccessError("拒绝写入无效或不可写范围 0x%08X+0x%X" %
                                        (actual, len(data)))
            restore_protection = self.backend.protect(
                actual, len(data), PAGE_EXECUTE_READWRITE)
        try:
            transferred = self.backend.write(actual, data)
            if transferred != len(data):
                raise MemoryAccessError("部分写入 0x%08X，实际 %d/%d 字节" %
                                        (actual, transferred, len(data)))
            if verify and self.backend.read(actual, len(data)) != data:
                raise MemoryAccessError("写后复读不一致: 0x%08X" % actual)
        finally:
            if restore_protection is not None:
                self.backend.protect(actual, len(data), restore_protection)

    def write_actual_bytes(self, address: int, data: bytes,
                           verify: bool = True) -> None:
        self._check_open()
        if not self.validate_actual_range(address, len(data), write=True):
            raise MemoryAccessError("拒绝写入无效运行时范围 0x%08X+0x%X" %
                                    (address, len(data)))
        transferred = self.backend.write(address, data)
        if transferred != len(data):
            raise MemoryAccessError("运行时范围只写入了部分字节")
        if verify and self.backend.read(address, len(data)) != data:
            raise MemoryAccessError("运行时范围写后复读不一致")

    def write_u8(self, address: int, value: int) -> None:
        self._check_value(value, 8)
        self.write_bytes(address, struct.pack("<B", value))

    def write_u16(self, address: int, value: int) -> None:
        self._check_value(value, 16)
        self.write_bytes(address, struct.pack("<H", value))

    def write_u32(self, address: int, value: int) -> None:
        self._check_value(value, 32)
        self.write_bytes(address, struct.pack("<I", value))

    def write_transaction(self, entries) -> None:
        """Write data ranges atomically, restoring earlier ranges on failure."""
        prepared = []
        seen = []
        for address, data in entries:
            if not isinstance(data, bytes) or not data:
                raise MemoryAccessError("事务写入数据必须是非空 bytes")
            actual = self.resolve_reference(int(address))
            current_range = (actual, actual + len(data))
            if any(current_range[0] < end and start < current_range[1]
                   for start, end in seen):
                raise MemoryAccessError("事务写入范围不能重叠")
            if not self.validate_actual_range(actual, len(data), write=True):
                raise MemoryAccessError("事务写入范围无效或不可写: 0x%08X" % actual)
            previous = self.backend.read(actual, len(data))
            prepared.append((int(address), data, previous))
            seen.append(current_range)
        changed = []
        try:
            for address, data, previous in prepared:
                self.write_bytes(address, data)
                changed.append((address, previous))
        except Exception:
            for address, previous in reversed(changed):
                try:
                    self.write_bytes(address, previous)
                except Exception:
                    pass
            raise

    @staticmethod
    def _check_value(value: int, width: int) -> None:
        if not isinstance(value, int) or not 0 <= value < (1 << width):
            raise ValueError("数值超出 UInt%d 范围" % width)

    def set_patch(self, spec: PatchSpec, enabled: bool) -> None:
        if enabled:
            self._enable_patch(spec)
        else:
            self._disable_patch(spec)

    @staticmethod
    def _rel32(source_after: int, target: int) -> bytes:
        displacement = int(target) - int(source_after)
        if not -(1 << 31) <= displacement < (1 << 31):
            raise PatchError("rel32 跳转距离超出范围")
        return struct.pack("<i", displacement)

    def _build_dynamic_stub(self, spec: DynamicPatchSpec,
                            allocation: int) -> bytes:
        stub = bytearray(spec.stub_template)
        for relocation in spec.relocations:
            if relocation.offset < 0 or relocation.offset + 4 > len(stub):
                raise PatchError("%s 的 stub 重定位越界" % spec.label)
            if relocation.kind == "absolute_reference":
                value = self.resolve_reference(relocation.value) + relocation.addend
                encoded = struct.pack("<I", value & 0xFFFFFFFF)
            elif relocation.kind == "absolute_u32":
                value = relocation.value + relocation.addend
                encoded = struct.pack("<I", value & 0xFFFFFFFF)
            elif relocation.kind == "relative_reference":
                target = self.resolve_reference(relocation.value) + relocation.addend
                encoded = self._rel32(allocation + relocation.offset + 4, target)
            elif relocation.kind == "relative_stub":
                target = allocation + relocation.value + relocation.addend
                encoded = self._rel32(allocation + relocation.offset + 4, target)
            else:
                raise PatchError("%s 使用未知 stub 重定位类型 %s" %
                                 (spec.label, relocation.kind))
            stub[relocation.offset:relocation.offset + 4] = encoded
        return bytes(stub)

    def _dynamic_branch(self, site, allocation: int,
                        allocation_size: int) -> bytes:
        if not 0 <= site.stub_offset < allocation_size:
            raise PatchError("动态调用点的 stub 入口偏移越界")
        actual_site = self.resolve_reference(site.address)
        target = allocation + site.stub_offset
        branch = bytes((site.branch_opcode,)) + self._rel32(actual_site + 5, target)
        return branch + b"\x90" * (site.instruction_length - 5)

    @staticmethod
    def _dynamic_owned_write(site, branch: bytes) -> Tuple[int, bytes, bytes]:
        if site.operand_only:
            if site.instruction_length != 5 or site.branch_opcode not in (0xE8, 0xE9):
                raise PatchError("rel32 操作数补丁必须对应五字节 CALL/JMP")
            return site.address + 1, branch[1:5], site.original[1:5]
        return site.address, branch, site.original

    @contextmanager
    def _quiesced_thread_eips(self):
        if hasattr(self.backend, "quiesced_thread_eips"):
            with self.backend.quiesced_thread_eips() as eips:
                yield eips
            return
        if self.pid is None:
            raise PatchError("动态 stub 会话缺少进程 ID")
        with suspended_thread_eips(self.pid) as eips:
            yield eips

    def set_dynamic_patch(self, spec: DynamicPatchSpec, enabled: bool) -> None:
        if enabled:
            self._enable_dynamic_patch(spec)
        else:
            self._disable_dynamic_patch(spec)

    def is_dynamic_patch_enabled(self, key: str) -> bool:
        """Return whether this session still owns every byte of a live stub."""
        lease = self._dynamic_leases.get(str(key))
        if lease is None:
            return False
        try:
            return all(self.read_bytes(site.address, len(branch)) == branch
                       for site, branch in zip(lease.spec.call_sites,
                                               lease.branch_bytes))
        except MemoryAccessError:
            return False

    def _enable_dynamic_patch(self, spec: DynamicPatchSpec) -> None:
        current_lease = self._dynamic_leases.get(spec.key)
        if current_lease is not None:
            for site, expected in zip(spec.call_sites, current_lease.branch_bytes):
                if self.read_bytes(site.address, len(expected)) != expected:
                    raise PatchError("%s已启用的调用点被外部修改" % spec.label)
            return
        for site in spec.call_sites:
            if self.read_bytes(site.address, len(site.original)) != site.original:
                raise PatchError("%s调用点原字节已变化" % spec.label)
        allocation = 0
        branches: Tuple[bytes, ...] = ()
        changed = []
        try:
            allocation = self.backend.allocate(len(spec.stub_template), PAGE_READWRITE)
            stub = self._build_dynamic_stub(spec, allocation)
            if self.backend.write(allocation, stub) != len(stub):
                raise PatchError("%s stub 只写入了部分字节" % spec.label)
            if self.backend.read(allocation, len(stub)) != stub:
                raise PatchError("%s stub 写后复读失败" % spec.label)
            self.backend.protect(allocation, len(stub), PAGE_EXECUTE_READ)
            if hasattr(self.backend, "flush"):
                self.backend.flush(allocation, len(stub))
            branches = tuple(self._dynamic_branch(
                site, allocation, len(stub)) for site in spec.call_sites)
            for site, branch in zip(spec.call_sites, branches):
                address, owned, _original = self._dynamic_owned_write(site, branch)
                self.write_bytes(address, owned, allow_protect=True)
                changed.append((site, branch))
            self._dynamic_leases[spec.key] = DynamicPatchLease(
                spec, allocation, len(stub), branches)
        except Exception:
            rollback_ok = True
            for site, branch in reversed(changed):
                try:
                    address, _owned, original = self._dynamic_owned_write(site, branch)
                    self.write_bytes(address, original, allow_protect=True)
                except Exception:
                    rollback_ok = False
            if allocation:
                if rollback_ok:
                    try:
                        self.backend.free(allocation)
                    except Exception:
                        self._orphaned_allocations.append(allocation)
                else:
                    self._orphaned_allocations.append(allocation)
            raise

    def _disable_dynamic_patch(self, spec: DynamicPatchSpec) -> None:
        lease = self._dynamic_leases.get(spec.key)
        if lease is None:
            if all(self.read_bytes(site.address, len(site.original)) == site.original
                   for site in spec.call_sites):
                return
            raise PatchError("%s并非由本工具启用，拒绝恢复" % spec.label)
        for site, expected in zip(spec.call_sites, lease.branch_bytes):
            if self.read_bytes(site.address, len(expected)) != expected:
                raise PatchError("%s调用点已被外部修改；保留 stub 到进程退出" %
                                 spec.label)
        with self._quiesced_thread_eips() as eips:
            if any(lease.allocation <= eip < lease.allocation + lease.allocation_size
                   for eip in eips):
                raise PatchError("%s仍有线程在 stub 内执行，拒绝释放" % spec.label)
            restored = []
            try:
                for site, branch in zip(spec.call_sites, lease.branch_bytes):
                    address, _owned, original = self._dynamic_owned_write(site, branch)
                    self.write_bytes(address, original, allow_protect=True)
                    restored.append((site, branch))
            except Exception:
                for site, branch in reversed(restored):
                    try:
                        address, owned, _original = self._dynamic_owned_write(site, branch)
                        self.write_bytes(address, owned, allow_protect=True)
                    except Exception:
                        pass
                raise
            self.backend.free(lease.allocation)
            self._dynamic_leases.pop(spec.key, None)

    def _enable_patch(self, spec: PatchSpec) -> None:
        states = []
        for site in spec.sites:
            current = self.read_bytes(site.address, len(site.original))
            if current not in (site.original, site.patched):
                raise PatchError("%s在 0x%08X 的原字节已被其它修改占用" %
                                 (spec.label, site.address))
            states.append(current)
        if spec.key not in self._active_patches:
            patched_count = sum(current == site.patched
                                for site, current in zip(spec.sites, states))
            if 0 < patched_count < len(spec.sites):
                raise PatchError("%s已有部分站点被外部修改，拒绝接管" % spec.label)
        changed = []
        try:
            for site, current in zip(spec.sites, states):
                if current != site.patched:
                    self.write_bytes(site.address, site.patched, allow_protect=True)
                    changed.append((site, current))
        except Exception:
            for site, previous in reversed(changed):
                try:
                    self.write_bytes(site.address, previous, allow_protect=True)
                except Exception:
                    pass
            raise
        if spec.key in self._active_patches or all(
                current == site.original for site, current in zip(spec.sites, states)):
            self._active_patches[spec.key] = spec

    def _disable_patch(self, spec: PatchSpec) -> None:
        if spec.key not in self._active_patches:
            if all(self.read_bytes(site.address, len(site.original)) == site.original
                   for site in spec.sites):
                return
            raise PatchError("%s并非由本工具启用，拒绝恢复" % spec.label)
        states = []
        for site in spec.sites:
            current = self.read_bytes(site.address, len(site.patched))
            if current != site.patched:
                raise PatchError("%s在 0x%08X 已被外部修改，拒绝误恢复" %
                                 (spec.label, site.address))
            states.append(current)
        changed = []
        try:
            for site in spec.sites:
                self.write_bytes(site.address, site.original, allow_protect=True)
                changed.append(site)
        except Exception:
            for site in reversed(changed):
                try:
                    self.write_bytes(site.address, site.patched, allow_protect=True)
                except Exception:
                    pass
            raise
        self._active_patches.pop(spec.key, None)

    @contextmanager
    def remote_backend(self):
        """Acquire create-thread permission only for the duration of a call."""
        if isinstance(self.backend, FakeMemoryBackend):
            yield self.backend
            return
        if self.pid is None:
            raise MemoryAccessError("当前会话缺少进程 ID，不能创建远程线程")
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        access = (PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION |
                  PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE |
                  SYNCHRONIZE)
        handle = kernel32.OpenProcess(access, False, int(self.pid))
        if not handle:
            raise MemoryAccessError("申请远程调用权限失败，WinError=%d" % ctypes.get_last_error())
        backend = Win32Backend(int(handle))
        try:
            yield backend
        finally:
            backend.close()

    def ReadProcessMemory(self, _handle, address, buffer, size, transferred) -> int:
        try:
            target = getattr(buffer, "_obj", None)
            if target is not None:
                ctypes.memset(ctypes.addressof(target), 0, ctypes.sizeof(target))
            data = self.read_bytes(int(address), int(size))
            ctypes.memmove(buffer, data, len(data))
            if transferred:
                ctypes.cast(transferred, ctypes.POINTER(ctypes.c_size_t))[0] = len(data)
            self.last_error = ""
            return 1
        except Exception as exc:
            self.last_error = "读取 0x%08X+0x%X 失败: %s" % (
                int(address), int(size), exc)
            if callable(self.error_handler):
                self.error_handler(self.last_error)
            return 0

    def WriteProcessMemory(self, _handle, address, buffer, size, transferred) -> int:
        try:
            data = ctypes.string_at(buffer, int(size))
            actual = self.resolve_reference(int(address))
            in_module = self.module_base <= actual < self.module_base + self.module_size
            self.write_bytes(int(address), data, allow_protect=in_module)
            if transferred:
                ctypes.cast(transferred, ctypes.POINTER(ctypes.c_size_t))[0] = len(data)
            self.last_error = ""
            return 1
        except Exception as exc:
            self.last_error = "写入 0x%08X+0x%X 失败: %s" % (
                int(address), int(size), exc)
            if callable(self.error_handler):
                self.error_handler(self.last_error)
            return 0

    def close(self, restore_patches: bool = True) -> None:
        if self.closed:
            return
        if restore_patches:
            for lease in list(self._dynamic_leases.values())[::-1]:
                try:
                    self._disable_dynamic_patch(lease.spec)
                except Exception:
                    pass
            for spec in list(self._active_patches.values())[::-1]:
                try:
                    self._disable_patch(spec)
                except Exception:
                    pass
        self.closed = True
        if self.owns_handle:
            self.backend.close()
        self.handle = 0

    def __enter__(self) -> "MemorySession":
        return self

    def __exit__(self, _exc_type, _exc, _traceback) -> None:
        self.close()


@dataclass
class FakeRegion:
    base: int
    data: bytearray
    protection: int = PAGE_READWRITE


class FakeMemoryBackend:
    """Deterministic backend used by the standard-library unit tests."""

    def __init__(self, base: int, data: bytes,
                 protection: int = PAGE_READWRITE):
        self.region = FakeRegion(base, bytearray(data), protection)
        self.fail_write_at: Optional[int] = None
        self.partial_write_at: Optional[int] = None
        self.closed = False
        self.allocations: Dict[int, int] = {}
        self.freed = []
        self.closed_threads = []
        self.waited_threads = []
        self._next_thread = 1
        self.flushed = []
        self.active_eips = []

    def _slice(self, address: int, size: int) -> slice:
        start = address - self.region.base
        if start < 0 or start + size > len(self.region.data):
            raise MemoryAccessError("假内存越界")
        return slice(start, start + size)

    def read(self, address: int, size: int) -> bytes:
        return bytes(self.region.data[self._slice(address, size)])

    def write(self, address: int, data: bytes) -> int:
        if self.fail_write_at == address:
            raise MemoryAccessError("模拟写入失败")
        count = len(data) - 1 if self.partial_write_at == address and len(data) > 1 else len(data)
        target = self._slice(address, count)
        self.region.data[target] = data[:count]
        return count

    def flush(self, address: int, size: int) -> None:
        self.flushed.append((address, size))

    def query(self, address: int) -> Tuple[int, int, int, int]:
        if not self.region.base <= address < self.region.base + len(self.region.data):
            raise MemoryAccessError("假内存页不存在")
        return self.region.base, len(self.region.data), MEM_COMMIT, self.region.protection

    def protect(self, _address: int, _size: int, protection: int) -> int:
        old = self.region.protection
        self.region.protection = protection
        return old

    def allocate(self, size: int, protection: int = PAGE_READWRITE) -> int:
        address = self.region.base + len(self.region.data)
        self.region.data.extend(b"\0" * size)
        self.region.protection = protection
        self.allocations[address] = size
        return address

    @contextmanager
    def quiesced_thread_eips(self):
        yield tuple(self.active_eips)

    def free(self, address: int) -> None:
        if address not in self.allocations:
            raise MemoryAccessError("释放未知的假远程内存")
        self.freed.append(address)
        del self.allocations[address]

    def create_thread(self, _start: int, _parameter: int) -> int:
        thread = self._next_thread
        self._next_thread += 1
        return thread

    def wait_thread(self, thread: int, _timeout_ms: int) -> None:
        self.waited_threads.append(thread)

    def close_thread(self, thread: int) -> None:
        self.closed_threads.append(thread)

    def close(self) -> None:
        self.closed = True
