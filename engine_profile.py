"""Engine identification and capability data for the CaoCaoZhuan modifier.

Addresses in this module are reference virtual addresses (VA) for the original
0x00400000 image.  Runtime users must resolve them through MemorySession.
"""

from __future__ import annotations

import hashlib
import os
import struct
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from capability_evidence import (CapabilityState, EvidenceError,
                                 EvidenceRepository, FeatureCapability,
                                 recipe_id)


REFERENCE_IMAGE_BASE = 0x00400000
IMAGE_FILE_MACHINE_I386 = 0x014C
PE32_MAGIC = 0x010B
ITEM_ROW_SIZE_66 = 0x19
ITEM_LOW_OFFSET_66 = 33164
ITEM_LOW_COUNT_66 = 104
ITEM_HIGH_OFFSET_66 = 0
ITEM_HIGH_COUNT_66 = 151
ITEM_RECORD_COUNT_66 = ITEM_LOW_COUNT_66 + ITEM_HIGH_COUNT_66
EQUIPMENT_COUNT_66 = 160
CONSUMABLE_ID_MIN_66 = 160
CONSUMABLE_ID_MAX_66 = 199
CONSUMABLE_STORAGE_COUNT_66 = 352
EFFECT_ROW_SIZE_66 = 0x10
EFFECT_CHARACTER_SLOTS_66 = 4
EFFECT_JOB_SLOTS_66 = 2
EFFECT_CHARACTER_COUNT_66 = 1024
EFFECT_EMPTY_CHARACTER_66 = EFFECT_CHARACTER_COUNT_66
EFFECT_EMPTY_CHARACTER_VALUES_66 = (1024, 1025)
EFFECT_JOB_COUNT_66 = 80


class ProfileError(RuntimeError):
    pass


@dataclass(frozen=True)
class PatchSite:
    address: int
    original: bytes
    patched: bytes

    def __post_init__(self) -> None:
        if not self.original or len(self.original) != len(self.patched):
            raise ValueError("补丁原字节与目标字节必须等长且不能为空")


@dataclass(frozen=True)
class PatchSpec:
    key: str
    label: str
    sites: Tuple[PatchSite, ...]
    signature_patterns: Tuple[str, ...] = ()
    normalized_fingerprint: str = ""
    instruction_lengths: Tuple[int, ...] = ()
    rollback_rule: str = "owned-bytes-only"

    def recipe(self) -> Dict[str, object]:
        return {
            "kind": "patch",
            "signaturePatterns": list(self.signature_patterns),
            "normalizedFingerprint": self.normalized_fingerprint,
            "instructionLengths": list(self.instruction_lengths),
            "rollbackRule": self.rollback_rule,
            "sites": [{
                "originalHex": item.original.hex().upper(),
                "patchedHex": item.patched.hex().upper(),
            } for item in self.sites],
        }


@dataclass(frozen=True)
class DynamicCallSite:
    address: int
    original: bytes
    instruction_length: int
    branch_opcode: int
    stub_offset: int = 0
    operand_only: bool = False

    def __post_init__(self) -> None:
        if self.instruction_length < 5 or len(self.original) != self.instruction_length:
            raise ValueError("动态调用点必须覆盖至少 5 个完整指令字节")
        if self.branch_opcode not in (0xE8, 0xE9):
            raise ValueError("动态调用点只支持 CALL/JMP rel32")


@dataclass(frozen=True)
class StubRelocation:
    offset: int
    kind: str
    value: int
    addend: int = 0


@dataclass(frozen=True)
class DynamicPatchSpec:
    key: str
    label: str
    call_sites: Tuple[DynamicCallSite, ...]
    stub_template: bytes
    relocations: Tuple[StubRelocation, ...] = ()
    signature_patterns: Tuple[str, ...] = ()
    normalized_fingerprint: str = ""
    rollback_rule: str = "owned-branches-and-no-eip-in-stub"

    def recipe(self) -> Dict[str, object]:
        return {
            "kind": "dynamic-stub",
            "signaturePatterns": list(self.signature_patterns),
            "normalizedFingerprint": self.normalized_fingerprint,
            "rollbackRule": self.rollback_rule,
            "stubTemplateHex": self.stub_template.hex().upper(),
            "relocations": [{
                "offset": item.offset,
                "kind": item.kind,
                "value": item.value,
                "addend": item.addend,
            } for item in self.relocations],
            "callSites": [{
                "originalHex": item.original.hex().upper(),
                "instructionLength": item.instruction_length,
                "branchOpcode": item.branch_opcode,
                "stubOffset": item.stub_offset,
                "operandOnly": item.operand_only,
            } for item in self.call_sites],
        }


AUTO_RETURN_GATE_PATTERN_66 = (
    "38 02 75 1C E8 ?? ?? ?? ?? 85 C0 74 13 8B 4D FC "
    "E8 ?? ?? ?? ?? B8 01 00 00 00")
AUTO_RETURN_STATE_PATTERN_66 = (
    "E8 ?? ?? ?? ?? 84 C0 74 02 B0 01 34 01 8B 4D DC "
    "0F B6 51 04 81 C2 ?? ?? ?? ?? 80 3A FF 90 74 02 88 02")
AUTO_RETURN_EFFECT_PATTERN_66 = (
    "55 8B EC 6A 01 6A 01 6A 5A 6A 38 E8 ?? ?? ?? ?? 5D C3")


def _relative_call_target(image: "PEImage", address: int) -> int:
    instruction = image.read_va(address, 5)
    if instruction[0] != 0xE8:
        raise ProfileError("0x%08X 不是 CALL rel32" % address)
    return address + 5 + struct.unpack("<i", instruction[1:5])[0]


def locate_auto_return_patch_66(image: "PEImage") -> Tuple[
        Optional[PatchSpec], Dict[str, object], str]:
    """Locate the native second-action gates used by 6.6 auto return."""
    patterns = {
        "gate": AUTO_RETURN_GATE_PATTERN_66,
        "state": AUTO_RETURN_STATE_PATTERN_66,
        "effect": AUTO_RETURN_EFFECT_PATTERN_66,
    }
    hits: Dict[str, int] = {}
    for name, pattern in patterns.items():
        matches = image.find_signature(MaskedSignature.parse(pattern))
        if len(matches) != 1:
            return None, {}, "自动回归%s签名匹配数为%d" % (name, len(matches))
        hits[name] = matches[0]

    gate_call = hits["gate"] + 4
    state_call = hits["state"]
    try:
        targets = (_relative_call_target(image, gate_call),
                   _relative_call_target(image, state_call))
    except ProfileError as exc:
        return None, {}, "自动回归调用关系解析失败: %s" % exc
    if targets[0] != hits["effect"] or targets[1] != hits["effect"]:
        return None, {}, "自动回归两个调用点未共同指向原生二次行动函数"

    site_data = (
        (hits["gate"] + 0x0B, b"\x74\x13"),
        (hits["state"] + 0x07, b"\x74\x02"),
        (hits["state"] + 0x1E, b"\x74\x02"),
    )
    try:
        for address, original in site_data:
            if image.read_va(address, len(original)) != original:
                return None, {}, "自动回归站点0x%08X原字节不匹配" % address
    except ProfileError as exc:
        return None, {}, "自动回归补丁点读取失败: %s" % exc

    fingerprint = hashlib.sha256(
        b"native-second-action-unrestricted-v1\0" +
        image.read_va(hits["effect"], 18) +
        b"".join(original for _address, original in site_data)
    ).hexdigest().upper()
    spec = PatchSpec(
        "control_auto_return", "自动回归",
        tuple(PatchSite(address, original, b"\x90\x90")
              for address, original in site_data),
        tuple(patterns.values()), fingerprint, (2, 2, 2))
    contract = {
        "mode": "native-second-action-unrestricted",
        "callSites": [gate_call, state_call],
        "nativeEffect": hits["effect"],
        "patchSites": [address for address, _original in site_data],
        "originalBytes": [original for _address, original in site_data],
        "patchedBytes": [b"\x90\x90"] * 3,
        "signatureHits": hits,
        "fingerprint": fingerprint,
    }
    return spec, contract, ""


def locate_consumable_mapping_66(
        image: "PEImage") -> Tuple[Optional[int], Dict[str, object], str]:
    """Locate the shared 6.6 item-count array from three independent users."""
    patterns = {
        "update": (
            "55 8B EC 2D A0 00 00 00 05 ?? ?? ?? ?? 84 C9 74 08 "
            "38 08 72 0B FE 08 EB 07 80 38 FF 74 02 FE 00 5D C3", 9),
        "read": (
            "55 8B EC 0F B7 C0 2D A0 00 00 00 0F B6 80 ?? ?? ?? ?? "
            "5D C3", 14),
        "write": (
            "55 8B EC 2D A0 00 00 00 8A 4D 08 88 88 ?? ?? ?? ?? 5D "
            "C2 04 00", 13),
        "clear": (
            "33 C0 99 66 3D 60 01 73 09 88 90 ?? ?? ?? ?? 40 EB F1", 11),
    }
    locations: Dict[str, int] = {}
    bases: Dict[str, int] = {}
    for name, (pattern, operand_offset) in patterns.items():
        hits = image.find_signature(MaskedSignature.parse(pattern))
        if len(hits) != 1:
            return None, {}, "6.6道具数量%s签名匹配数为%d" % (name, len(hits))
        locations[name] = hits[0]
        bases[name] = struct.unpack(
            "<I", image.read_va(hits[0] + operand_offset, 4))[0]
    if len(set(bases.values())) != 1:
        return None, {}, "6.6道具数量读写函数未指向同一基址"
    base = next(iter(bases.values()))
    mapping: Dict[str, object] = {
        "idMin": CONSUMABLE_ID_MIN_66,
        "idMax": CONSUMABLE_ID_MAX_66,
        "storageIdMax": CONSUMABLE_ID_MIN_66 + CONSUMABLE_STORAGE_COUNT_66 - 1,
        "storageCount": CONSUMABLE_STORAGE_COUNT_66,
        "stride": 1,
        "width": 1,
        "baseDereference": False,
        "itemIds": list(range(CONSUMABLE_ID_MIN_66,
                              CONSUMABLE_ID_MAX_66 + 1)),
        "locations": locations,
        "patterns": {name: value[0] for name, value in patterns.items()},
    }
    return base, mapping, ""


@dataclass(frozen=True)
class RemoteCallSpec:
    key: str
    label: str
    address: int
    signature: bytes
    abi_verified: bool = True
    signature_pattern: str = ""
    normalized_fingerprint: str = ""
    calling_convention: str = "unknown"
    ecx_source: str = ""
    arguments: Tuple[str, ...] = ()
    callee_cleanup: int = 0
    preconditions: Tuple[str, ...] = ()
    postconditions: Tuple[str, ...] = ()
    context_reference: int = 0
    wrapper_kind: str = ""

    def recipe(self) -> Dict[str, object]:
        return {
            "kind": "remote-call",
            "signaturePattern": self.signature_pattern,
            "normalizedFingerprint": self.normalized_fingerprint,
            "callingConvention": self.calling_convention,
            "ecxSource": self.ecx_source,
            "arguments": list(self.arguments),
            "calleeCleanup": self.callee_cleanup,
            "preconditions": list(self.preconditions),
            "postconditions": list(self.postconditions),
            "contextReference": self.context_reference,
            "wrapperKind": self.wrapper_kind,
        }


@dataclass(frozen=True)
class ItemRow66:
    name: str
    icon: int
    effect_or_type: int
    equipment_effect_or_category: int
    price: int
    ability: int
    effect_value: int
    growth: int
    catalog_flag: int

    @property
    def is_treasure(self) -> bool:
        return self.catalog_flag == 1


@dataclass(frozen=True)
class EffectAssignmentSlot66:
    target_id: int
    effect_value: int

    def __post_init__(self) -> None:
        if not 0 <= self.target_id <= 0xFFFF:
            raise ValueError("6.6特效目标 ID 超出 UInt16 范围")
        if not 0 <= self.effect_value <= 0xFF:
            raise ValueError("6.6特效值超出 UInt8 范围")


@dataclass(frozen=True)
class EffectAssignmentRow66:
    characters: Tuple[EffectAssignmentSlot66, ...]
    jobs: Tuple[EffectAssignmentSlot66, ...]

    def __post_init__(self) -> None:
        if len(self.characters) != EFFECT_CHARACTER_SLOTS_66:
            raise ValueError("6.6特效行必须包含 4 个角色槽")
        if len(self.jobs) != EFFECT_JOB_SLOTS_66:
            raise ValueError("6.6特效行必须包含 2 个兵种槽")
        if any(item.target_id > 0xFF for item in self.jobs):
            raise ValueError("6.6兵种 ID 超出 UInt8 范围")


def parse_effect_assignment_row_66(row: bytes) -> EffectAssignmentRow66:
    if len(row) != EFFECT_ROW_SIZE_66:
        raise ValueError("6.6特效分配行必须正好是 0x10 字节")
    characters = tuple(
        EffectAssignmentSlot66(
            struct.unpack_from("<H", row, index * 3)[0],
            row[index * 3 + 2])
        for index in range(EFFECT_CHARACTER_SLOTS_66))
    jobs = tuple(
        EffectAssignmentSlot66(row[0x0C + index * 2],
                               row[0x0D + index * 2])
        for index in range(EFFECT_JOB_SLOTS_66))
    return EffectAssignmentRow66(characters, jobs)


def encode_effect_assignment_row_66(row: EffectAssignmentRow66) -> bytes:
    result = bytearray()
    for item in row.characters:
        result.extend(struct.pack("<HB", item.target_id, item.effect_value))
    for item in row.jobs:
        result.extend(struct.pack("<BB", item.target_id, item.effect_value))
    if len(result) != EFFECT_ROW_SIZE_66:
        raise ValueError("6.6特效分配行编码长度错误")
    return bytes(result)


def detect_effect_empty_character_66(table: bytes) -> int:
    if len(table) % EFFECT_ROW_SIZE_66:
        raise ValueError("6.6特效分配表长度不是 0x10 的整数倍")
    sentinels = set()
    for offset in range(0, len(table), EFFECT_ROW_SIZE_66):
        row = parse_effect_assignment_row_66(
            table[offset:offset + EFFECT_ROW_SIZE_66])
        sentinels.update(item.target_id for item in row.characters
                         if item.target_id >= EFFECT_CHARACTER_COUNT_66)
    invalid = sentinels.difference(EFFECT_EMPTY_CHARACTER_VALUES_66)
    if invalid:
        raise ValueError("6.6特效表包含未知空角色值: %s" %
                         ", ".join(str(value) for value in sorted(invalid)))
    if len(sentinels) > 1:
        raise ValueError("6.6特效表混用了多个空角色值: %s" %
                         ", ".join(str(value) for value in sorted(sentinels)))
    return next(iter(sentinels), EFFECT_EMPTY_CHARACTER_66)


def parse_item_row_66(row: bytes) -> ItemRow66:
    if len(row) != 0x19:
        raise ValueError("6.6物品行必须正好是 0x19 字节")
    raw_name = row[0:0x0F].split(b"\0", 1)[0]
    try:
        name = raw_name.decode("gbk").rstrip("\r\n")
    except UnicodeDecodeError:
        name = "非法字符"
    return ItemRow66(name, row[0x0F], row[0x11], row[0x12], row[0x13],
                     row[0x15], row[0x16], row[0x17], row[0x18])


def treasure_ids_66(table: bytes,
                    equipment_count: int = EQUIPMENT_COUNT_66) -> List[int]:
    if len(table) % 0x19:
        raise ValueError("6.6物品表长度不是 0x19 的整数倍")
    count = min(len(table) // 0x19, int(equipment_count))
    return [index for index in range(count)
            if parse_item_row_66(table[index*0x19:(index+1)*0x19]).is_treasure]


def validate_item_table_66(table: bytes) -> bytes:
    expected = (ITEM_LOW_COUNT_66 + ITEM_HIGH_COUNT_66) * ITEM_ROW_SIZE_66
    if len(table) != expected:
        raise ProfileError("6.6物品表应为 255×0x19 字节，实际为 %d 字节" % len(table))
    if not any(table):
        raise ProfileError("6.6物品表为全零数据")
    named = 0
    decodable = 0
    for index in range(ITEM_LOW_COUNT_66 + ITEM_HIGH_COUNT_66):
        row = table[index*ITEM_ROW_SIZE_66:(index+1)*ITEM_ROW_SIZE_66]
        raw_name = row[:0x0F].split(b"\0", 1)[0]
        if not raw_name:
            continue
        named += 1
        try:
            raw_name.decode("gbk")
            decodable += 1
        except UnicodeDecodeError:
            pass
    if named < 128 or decodable < 128:
        raise ProfileError(
            "6.6物品表名称语义探针失败: 非空 %d，GBK可解码 %d" %
            (named, decodable))
    return table


def load_item_table_66(game_path: str) -> bytes:
    """Load the split 6.6 item rows without modifying game data files."""
    root = os.path.dirname(os.path.abspath(game_path)) if os.path.isfile(game_path) else os.path.abspath(game_path)
    low_path = os.path.join(root, "Data.e5")
    high_path = os.path.join(root, "Star.e5")
    try:
        with open(low_path, "rb") as stream:
            low_data = stream.read()
        with open(high_path, "rb") as stream:
            high_data = stream.read()
    except OSError as exc:
        raise ProfileError("6.6物品元数据文件不可读: %s" % exc) from exc
    low_end = ITEM_LOW_OFFSET_66 + ITEM_LOW_COUNT_66 * ITEM_ROW_SIZE_66
    high_end = ITEM_HIGH_OFFSET_66 + ITEM_HIGH_COUNT_66 * ITEM_ROW_SIZE_66
    if len(low_data) < low_end:
        raise ProfileError("Data.e5 长度不足，无法读取 0..103 物品行")
    if len(high_data) < high_end:
        raise ProfileError("Star.e5 长度不足，无法读取 104..254 物品行")
    table = (low_data[ITEM_LOW_OFFSET_66:low_end] +
             high_data[ITEM_HIGH_OFFSET_66:high_end])
    return validate_item_table_66(table)


@dataclass(frozen=True)
class MaskedSignature:
    """A byte signature where None represents one wildcard byte."""

    pattern: Tuple[Optional[int], ...]

    @classmethod
    def parse(cls, text: str) -> "MaskedSignature":
        values: List[Optional[int]] = []
        for part in text.split():
            values.append(None if part in ("?", "??") else int(part, 16))
        if not values:
            raise ValueError("签名不能为空")
        return cls(tuple(values))

    def find_all(self, data: bytes) -> List[int]:
        size = len(self.pattern)
        runs: List[Tuple[int, bytes]] = []
        run_start = 0
        run = bytearray()
        for index, value in enumerate(self.pattern + (None,)):
            if value is not None:
                if not run:
                    run_start = index
                run.append(value)
            elif run:
                runs.append((run_start, bytes(run)))
                run.clear()
        anchor_start, anchor = max(runs, key=lambda item: len(item[1]))
        hits: List[int] = []
        search_at = 0
        while True:
            anchor_hit = data.find(anchor, search_at)
            if anchor_hit < 0:
                break
            offset = anchor_hit - anchor_start
            if 0 <= offset <= len(data) - size and all(
                    expected is None or data[offset + index] == expected
                    for index, expected in enumerate(self.pattern)):
                hits.append(offset)
            search_at = anchor_hit + 1
        return hits


@dataclass(frozen=True)
class PESection:
    name: str
    virtual_address: int
    virtual_size: int
    raw_offset: int
    raw_size: int
    characteristics: int

    @property
    def executable(self) -> bool:
        return bool(self.characteristics & 0x20000000)


class PEImage:
    """Small dependency-free PE32 reader used by profile detection and tests."""

    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        with open(self.path, "rb") as stream:
            self.data = stream.read()
        if len(self.data) < 0x100 or self.data[:2] != b"MZ":
            raise ProfileError("目标文件不是有效的 PE 文件")
        pe_offset = self._u32(0x3C)
        if pe_offset + 24 > len(self.data) or self.data[pe_offset:pe_offset + 4] != b"PE\0\0":
            raise ProfileError("目标文件缺少 PE 头")
        self.machine = self._u16(pe_offset + 4)
        section_count = self._u16(pe_offset + 6)
        optional_size = self._u16(pe_offset + 20)
        optional = pe_offset + 24
        self.optional_magic = self._u16(optional)
        if self.optional_magic != PE32_MAGIC:
            raise ProfileError("扳手只支持 32 位 PE32 游戏进程")
        self.image_base = self._u32(optional + 28)
        self.size_of_image = self._u32(optional + 56)
        section_table = optional + optional_size
        self.sections: List[PESection] = []
        for index in range(section_count):
            offset = section_table + index * 40
            if offset + 40 > len(self.data):
                raise ProfileError("PE 节表已截断")
            raw_name = self.data[offset:offset + 8].split(b"\0", 1)[0]
            self.sections.append(PESection(
                raw_name.decode("ascii", errors="replace"),
                self._u32(offset + 12),
                self._u32(offset + 8),
                self._u32(offset + 20),
                self._u32(offset + 16),
                self._u32(offset + 36),
            ))

    def _u16(self, offset: int) -> int:
        return struct.unpack_from("<H", self.data, offset)[0]

    def _u32(self, offset: int) -> int:
        return struct.unpack_from("<I", self.data, offset)[0]

    @property
    def is_x86(self) -> bool:
        return self.machine == IMAGE_FILE_MACHINE_I386

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest().upper()

    def va_to_offset(self, va: int) -> int:
        rva = va - self.image_base
        for section in self.sections:
            span = max(section.virtual_size, section.raw_size)
            if section.virtual_address <= rva < section.virtual_address + span:
                delta = rva - section.virtual_address
                if delta >= section.raw_size:
                    raise ProfileError("地址位于未初始化 PE 数据区，文件中没有对应字节")
                return section.raw_offset + delta
        if 0 <= rva < min(len(self.data), 0x1000):
            return rva
        raise ProfileError("地址 0x%08X 不在 PE 文件映射范围内" % va)

    def offset_to_va(self, offset: int) -> int:
        for section in self.sections:
            if section.raw_offset <= offset < section.raw_offset + section.raw_size:
                return self.image_base + section.virtual_address + offset - section.raw_offset
        if 0 <= offset < 0x1000:
            return self.image_base + offset
        raise ProfileError("文件偏移 0x%X 不在 PE 节中" % offset)

    def read_va(self, va: int, size: int) -> bytes:
        if size <= 0:
            raise ProfileError("PE 读取长度必须大于零")
        offset = self.va_to_offset(va)
        rva = va - self.image_base
        for section in self.sections:
            if (section.virtual_address <= rva <
                    section.virtual_address + max(section.virtual_size,
                                                  section.raw_size)):
                delta = rva - section.virtual_address
                if delta + size > section.raw_size:
                    raise ProfileError("读取 PE 字节时越过当前文件后备节边界")
                break
        else:
            if rva + size > min(len(self.data), 0x1000):
                raise ProfileError("读取 PE 头时越过头部映射范围")
        result = self.data[offset:offset + size]
        if len(result) != size:
            raise ProfileError("读取 PE 字节时越过文件末尾")
        return result

    def find_signature(self, signature: MaskedSignature,
                       executable_only: bool = True) -> List[int]:
        hits: List[int] = []
        sections = [item for item in self.sections
                    if item.executable or not executable_only]
        for section in sections:
            raw = self.data[section.raw_offset:section.raw_offset + section.raw_size]
            for local_offset in signature.find_all(raw):
                hits.append(self.image_base + section.virtual_address + local_offset)
        return hits

    def find_literal_references(self, value: int,
                                executable_only: bool = True) -> List[int]:
        needle = struct.pack("<I", value)
        result: List[int] = []
        sections = [item for item in self.sections
                    if item.executable or not executable_only]
        for section in sections:
            raw = self.data[section.raw_offset:section.raw_offset + section.raw_size]
            start = 0
            while True:
                index = raw.find(needle, start)
                if index < 0:
                    break
                result.append(self.image_base + section.virtual_address + index)
                start = index + 1
        return result


@dataclass
class EngineProfile:
    version: int
    display_version: str
    variant_name: str
    sha256: str
    file_size: int
    preferred_image_base: int
    image_size: int
    addresses: Dict[str, int]
    limits: Dict[str, int]
    capabilities: Dict[str, FeatureCapability]
    patches: Dict[str, PatchSpec]
    remote_calls: Dict[str, RemoteCallSpec]
    runtime_probe_failures: Dict[str, str] = field(default_factory=dict)
    dynamic_patches: Dict[str, DynamicPatchSpec] = field(default_factory=dict)
    metadata: Dict[str, object] = field(default_factory=dict)
    force_unverified_66: bool = False

    @property
    def is_66(self) -> bool:
        return self.version == 6

    def capability(self, key: str) -> FeatureCapability:
        return self.capabilities.get(
            key, FeatureCapability(
                key, CapabilityState.UNAVAILABLE, "当前引擎画像未定义此功能",
                "PROFILE_UNDEFINED"))

    def can_use(self, key: str) -> bool:
        if self.is_66 and self.force_unverified_66:
            return True
        return self.capability(key).available

    def public_capabilities(self) -> List[FeatureCapability]:
        internal = {"person_r", "person_s", "person_face", "variables",
                    "variables_bool_anchor", "item_metadata",
                    "variables_bool_storage", "effect_query_layout"}
        return [item for key, item in self.capabilities.items()
                if key not in internal]

    def state_counts(self) -> Dict[CapabilityState, int]:
        result = {state: 0 for state in CapabilityState}
        for capability in self.public_capabilities():
            result[capability.state] += 1
        return result

    def available_count(self) -> Tuple[int, int]:
        values = self.public_capabilities()
        return sum(1 for item in values if item.available), len(values)

    def summary(self) -> str:
        counts = self.state_counts()
        if self.is_66 and self.force_unverified_66:
            public = self.public_capabilities()
            located = sum(1 for item in public if item.recipe_id)
            text = ("%s / %s / 强制试用 %d / 已定位 %d / 旧地址 %d" %
                    (self.display_version, self.variant_name, len(public),
                     located, len(public) - located))
        else:
            text = ("%s / %s / 已启用 %d / 实机已验证 %d / 仅静态 %d / 禁用 %d" %
                    (self.display_version, self.variant_name,
                     counts[CapabilityState.ENABLED],
                     counts[CapabilityState.RUNTIME_VERIFIED],
                     counts[CapabilityState.STATIC_VERIFIED],
                     counts[CapabilityState.UNAVAILABLE]))
        blocked = [item.reason for item in self.public_capabilities()
                   if item.state is not CapabilityState.ENABLED and item.reason]
        if blocked:
            text += " / " + blocked[0]
        return text

    def reference_va(self, key: str) -> int:
        return self.addresses[key]

    def item_table_66(self) -> bytes:
        if not self.is_66:
            raise ProfileError("当前引擎不是 6.6 物品布局")
        table = self.metadata.get("item_table_66")
        if not isinstance(table, bytes):
            raise ProfileError(self.capability("item_metadata").reason or
                               "6.6物品元数据当前不可用")
        return validate_item_table_66(table)

    def probe_runtime(self, memory) -> None:
        """Apply cheap structural probes without writing to the target."""
        if not self.is_66:
            return
        failures: Dict[str, str] = {}
        for key, patch in self.patches.items():
            try:
                for site in patch.sites:
                    current = memory.read_bytes(site.address, len(site.original))
                    if current not in (site.original, site.patched):
                        failures[key] = "%s运行时原字节已变化" % patch.label
                        break
            except Exception as exc:
                failures[key] = "%s运行时字节不可读: %s" % (patch.label, exc)
        for key, patch in self.dynamic_patches.items():
            try:
                for site in patch.call_sites:
                    current = memory.read_bytes(site.address, len(site.original))
                    if current != site.original and not memory.is_dynamic_patch_enabled(key):
                        failures[key] = "%s运行时调用点原字节已变化" % patch.label
                        break
            except Exception as exc:
                failures[key] = "%s运行时调用点不可读: %s" % (patch.label, exc)
        for key, call in self.remote_calls.items():
            if not call.signature:
                continue
            try:
                if memory.read_bytes(call.address, len(call.signature)) != call.signature:
                    failures[key] = "%s运行时函数签名已变化" % call.label
            except Exception as exc:
                failures[key] = "%s运行时函数不可读: %s" % (call.label, exc)
        try:
            first_id = memory.read_u16(self.addresses["battle_units"])
            if first_id != 0xFFFF and first_id >= self.limits["person_count"]:
                failures["battle"] = "战场单位 Data ID 探针失败"
            battle_count = (self.limits["battle_ours"] +
                            self.limits["battle_friends"] +
                            self.limits["battle_enemies"])
            if not memory.validate_range(
                    self.addresses["battle_units"],
                    battle_count * self.limits["battle_stride"], write=True):
                failures["battle"] = "战场单位表运行时页不可写"
        except Exception as exc:
            failures["battle"] = "战场单位表不可读: %s" % exc
        try:
            person_base = memory.read_u32(self.addresses["person_pointer"])
            if not memory.validate_actual_range(person_base, self.limits["person_stride"], write=True):
                failures["person"] = "人物数组运行时指针无效"
        except Exception as exc:
            failures["person"] = "人物数组指针不可读: %s" % exc
        try:
            fatal_base = memory.read_u32(self.addresses["fatal_pointer"])
            if not memory.validate_actual_range(fatal_base, 16, write=True):
                failures["fatal"] = "必杀分配运行时指针无效"
            else:
                self.addresses["fatal_table"] = fatal_base
        except Exception as exc:
            failures["fatal"] = "必杀分配指针不可读: %s" % exc
        try:
            if not memory.validate_range(
                    self.addresses["warehouse"],
                    self.limits["warehouse_count"] * 3, write=True):
                failures["warehouse"] = "仓库表运行时页不可写"
        except Exception as exc:
            failures["warehouse"] = "仓库结构探针失败: %s" % exc
        try:
            self.item_table_66()
        except (ProfileError, ValueError) as exc:
            failures["item_metadata"] = "6.6物品元数据探针失败: %s" % exc
        consumable = self.capabilities.get("item_consumables")
        if consumable is not None and consumable.statically_verified:
            try:
                mapping = self.metadata["consumable_mapping"]
                count_base = self.addresses["consumable_counts"]
                if mapping.get("baseDereference"):
                    count_base = memory.read_u32(count_base)
                    valid = memory.validate_actual_range(
                        count_base,
                        (int(mapping["idMax"]) - int(mapping["idMin"])) *
                        int(mapping["stride"]) + int(mapping["width"]), write=True)
                else:
                    valid = memory.validate_range(
                        count_base,
                        (int(mapping["idMax"]) - int(mapping["idMin"])) *
                        int(mapping["stride"]) + int(mapping["width"]), write=True)
                if not valid:
                    failures["item_consumables"] = "消耗品计数表运行时页不可写"
            except Exception as exc:
                failures["item_consumables"] = "消耗品映射运行时探针失败: %s" % exc
        try:
            self.addresses["effect_assign"] = 0
            effect_base = memory.read_u32(
                self.addresses["effect_assign_pointer"])
            effect_size = (self.limits["effect_count"] *
                           self.limits["effect_stride"])
            if not memory.validate_actual_range(
                    effect_base, effect_size, write=True):
                failures["effect"] = (
                    "特效分配表运行时指针无效: 0x%08X" % effect_base)
            else:
                effect_table = memory.read_actual_bytes(effect_base, effect_size)
                self.metadata["effect_empty_character"] = (
                    detect_effect_empty_character_66(effect_table))
                self.addresses["effect_assign"] = effect_base
            if not memory.validate_range(
                    self.addresses["exclusive_set"],
                    self.limits["effect_count"] * 16, write=True):
                failures["effect"] = "专属/套装表运行时页不可写"
        except Exception as exc:
            failures["effect"] = "特效结构探针失败: %s" % exc
        for address_key, capability_key in (
                ("bool_vars", "variables_bool"),
                ("int_vars", "variables_int"),
                ("ptr_vars", "variables_ptr")):
            try:
                layout = self.metadata["variable_layouts"][capability_key]
                base = self.addresses[address_key]
                count_offset = layout.get("countOffset")
                if count_offset is not None:
                    actual_count = memory.read_u32(base + int(count_offset))
                    if actual_count != self.limits["variable_count"]:
                        failures[capability_key] = (
                            "%s数量头为 %d，预期 %d" %
                            (address_key, actual_count,
                             self.limits["variable_count"]))
                        continue
                size = (int(layout["dataOffset"]) +
                        ((self.limits["variable_count"] + 7) // 8
                         if layout.get("storage") == "bitset" else
                         (self.limits["variable_count"] - 1) *
                         int(layout["stride"]) + int(layout["width"])))
                if not memory.validate_range(
                        base, size, write=True):
                    failures[capability_key] = "%s运行时页不可写" % address_key
            except Exception as exc:
                failures[capability_key] = "变量表结构探针失败: %s" % exc
        self.runtime_probe_failures = failures
        for key, reason in failures.items():
            current = self.capabilities.get(key)
            if current and current.statically_verified:
                self.capabilities[key] = current.disable(
                    reason, "RUNTIME_PROBE_FAILED")
        if "warehouse" in failures:
            current = self.capabilities["item_bulk_treasure"]
            self.capabilities["item_bulk_treasure"] = current.disable(
                failures["warehouse"], "DEPENDENCY_RUNTIME_PROBE_FAILED")
        if "item_metadata" in failures:
            for key in ("item_metadata", "item_bulk_treasure"):
                current = self.capabilities.get(key)
                if current is not None:
                    self.capabilities[key] = current.disable(
                        failures["item_metadata"], "ITEM_METADATA_PROBE_FAILED")
        if "person" in failures:
            current = self.capabilities["recalculate"]
            self.capabilities["recalculate"] = current.disable(
                failures["person"], "DEPENDENCY_RUNTIME_PROBE_FAILED")
        if "battle" in failures:
            current = self.capabilities["revive"]
            self.capabilities["revive"] = current.disable(
                failures["battle"], "DEPENDENCY_RUNTIME_PROBE_FAILED")

        for key, current in list(self.capabilities.items()):
            if (key not in failures and
                    current.state is CapabilityState.RUNTIME_VERIFIED):
                self.capabilities[key] = current.promote(CapabilityState.ENABLED)

        for key, call in list(self.remote_calls.items()):
            capability = self.capabilities.get(key)
            if capability is not None and capability.available and not call.abi_verified:
                self.remote_calls[key] = RemoteCallSpec(
                    call.key, call.label, call.address, call.signature, True,
                    call.signature_pattern, call.normalized_fingerprint,
                    call.calling_convention, call.ecx_source, call.arguments,
                    call.callee_cleanup, call.preconditions, call.postconditions,
                    call.context_reference, call.wrapper_kind)


KNOWN_66 = {
    "88EC708A24718868090F70256D09086E83C92FAB0613C7B8D3742EF974D3564D":
        ("清儿吕布传", 1413120),
    "4A4FD8DDBF83E5F0B769D1B97BF8F6E6431C3AB42892024A354228212D3D06A4":
        ("新改曹操傳6.6修正版", 1130496),
}
_BASELINE_SHA256 = tuple(KNOWN_66)
_EVIDENCE_REPOSITORY = EvidenceRepository()


_PATCH_LOCATORS = {
    "control_all_factions": (
        ("E8 ?? ?? ?? ?? 3B 45 F0 74 0F 8B 4D F4 03 4D F8", 8,
         b"\x74\x0F", b"\x90\x90", 2),
        ("8B 55 F4 3B 55 EC 74 34 8B 4D F0 E8 ?? ?? ?? ??", 6,
         b"\x74\x34", b"\x90\x90", 2),
        ("5A 33 C9 3B D0 0F 94 C1 39 4D DC 75 27 0F B7 45 0C", 11,
         b"\x75\x27", b"\x90\x90", 2),
        ("90 90 90 90 90 90 3B F0 75 23 68 ?? ?? ?? ?? E8", 8,
         b"\x75\x23", b"\xEB\x23", 2),
    ),
    "control_friendly": (
        ("DC E8 ?? ?? ?? ?? 3C 01 74 14 33 C0 A0 30 42 4B 00", 8, b"\x74", b"\xEB", 2),
        ("DC E8 ?? ?? ?? ?? 3C 07 74 15 33 C9 8A 0D 30 42 4B 00", 8, b"\x74", b"\xEB", 2),
        ("F8 E8 ?? ?? ?? ?? 3C 07 74 15 33 C0 A0 30 42 4B 00", 8, b"\x74", b"\xEB", 2),
        ("D8 E8 ?? ?? ?? ?? 3C 02 75 C8 8B 4D D8 E8", 8, b"\x75\xC8", b"\x90\x90", 2),
        ("D8 E8 ?? ?? ?? ?? 3C 07 75 BC 8B 4D D8 E8", 8, b"\x75\xBC", b"\x90\x90", 2),
        ("E4 E8 ?? ?? ?? ?? 3C 07 74 18 33 C0 A0 30 42 4B 00", 8, b"\x74", b"\xEB", 2),
    ),
    "control_no_ai": (
        ("E0 E8 ?? ?? ?? ?? 3C 07 74 B8 6A 04 8B 4D E0", 8, b"\x74", b"\xEB", 2),
    ),
    "control_move_after_wait": (
        ("DC E8 ?? ?? ?? ?? 85 C0 74 04 C6 45 FC 06", 8, b"\x74", b"\xEB", 2),
    ),
    "control_move_255": (
        ("51 14 8B E5 5D C2 04 00 55 8B EC 83 EC 08 89 4D F8", 8,
         b"\x55\x8B\xEC\x83\xEC\x08", b"\x33\xC0\x48\xC3\x90\x90", 6),
    ),
    "control_pass_through": (
        ("FC E8 ?? ?? ?? ?? 85 D2 74 11 83 7D F0 01", 8, b"\x74", b"\xEB", 2),
        ("90 90 90 90 90 90 90 90 55 8B EC 51 52 50 33 D2", 8,
         b"\x55\x8B\xEC", b"\x33\xC0\xC3", 3),
    ),
}


def _locate_patch(image: PEImage, key: str, label: str) -> Tuple[Optional[PatchSpec], str]:
    sites: List[PatchSite] = []
    patterns: List[str] = []
    instruction_lengths: List[int] = []
    for pattern, target_offset, original, patched, instruction_length in _PATCH_LOCATORS[key]:
        hits = image.find_signature(MaskedSignature.parse(pattern))
        if len(hits) != 1:
            return None, "%s签名匹配数为 %d" % (label, len(hits))
        address = hits[0] + target_offset
        current = image.read_va(address, len(original))
        if current != original:
            return None, "%s原字节不匹配" % label
        sites.append(PatchSite(address, original, patched))
        patterns.append(pattern)
        instruction_lengths.append(instruction_length)
    fingerprint = hashlib.sha256("|".join(patterns).encode("ascii")).hexdigest().upper()
    return PatchSpec(key, label, tuple(sites), tuple(patterns), fingerprint,
                     tuple(instruction_lengths)), ""


def _capability(key: str, static_verified: bool, reason: str = "",
                recipe: Optional[Dict[str, object]] = None,
                reason_code: str = "", **addresses: int) -> FeatureCapability:
    if not static_verified:
        return FeatureCapability(
            key, CapabilityState.UNAVAILABLE, reason or "静态验证未通过",
            reason_code or "STATIC_VERIFICATION_FAILED", "", (), addresses)
    current_recipe = recipe or {
        "kind": "profile-contract",
        "feature": key,
        "addresses": {name: value for name, value in sorted(addresses.items())},
    }
    current_recipe_id = recipe_id(key, current_recipe)
    capability = FeatureCapability(
        key, CapabilityState.STATIC_VERIFIED,
        "静态签名已通过，等待双基底实机证据", "RUNTIME_EVIDENCE_REQUIRED",
        current_recipe_id, (), addresses, current_recipe)
    try:
        verified = _EVIDENCE_REPOSITORY.verified_recipe(key, _BASELINE_SHA256)
    except EvidenceError as exc:
        return capability.with_state(
            CapabilityState.STATIC_VERIFIED,
            reason="证据清单无效，保持仅静态确认: %s" % exc,
            reason_code="EVIDENCE_INVALID")
    if verified is not None and verified.recipe_id == current_recipe_id:
        return capability.with_state(
            CapabilityState.RUNTIME_VERIFIED,
            reason="双基底实机证据已通过，等待当前进程探针",
            reason_code="SESSION_PROBE_REQUIRED",
            evidence_ids=verified.evidence_ids)
    return capability


def _recipe_bytes(value: object, label: str) -> bytes:
    try:
        result = bytes.fromhex(str(value))
    except ValueError as exc:
        raise ProfileError("证据配方中的%s不是合法十六进制" % label) from exc
    if not result:
        raise ProfileError("证据配方中的%s不能为空" % label)
    return result


def _recipe_int(value: object, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, str):
        return int(value, 0)
    return int(value)


def _recipe_locator(image: PEImage, locator: Dict[str, object],
                    label: str) -> Tuple[int, str]:
    pattern = str(locator.get("pattern", ""))
    if not pattern:
        raise ProfileError("%s证据配方缺少定位签名" % label)
    hits = image.find_signature(MaskedSignature.parse(pattern))
    if len(hits) != 1:
        raise ProfileError("%s证据签名匹配数为 %d" % (label, len(hits)))
    return hits[0] + _recipe_int(locator.get("targetOffset"), 0), pattern


def _materialize_verified_recipes(
        image: PEImage, capabilities: Dict[str, FeatureCapability],
        patches: Dict[str, PatchSpec], dynamic_patches: Dict[str, DynamicPatchSpec],
        remote_calls: Dict[str, RemoteCallSpec], addresses: Dict[str, int],
        limits: Dict[str, int], metadata: Dict[str, object]) -> None:
    labels = {
        "control_all_factions": "不分敌我",
        "control_auto_return": "自动回归",
        "turn_refresh_direction": "转向刷新",
        "turn_refresh_position": "坐标刷新",
        "item_consumables": "消耗品计数",
    }
    for key, label in labels.items():
        try:
            verified = _EVIDENCE_REPOSITORY.verified_recipe(key, _BASELINE_SHA256)
        except EvidenceError as exc:
            capabilities[key] = capabilities[key].with_state(
                CapabilityState.UNAVAILABLE,
                reason="证据清单无效: %s" % exc,
                reason_code="EVIDENCE_INVALID")
            continue
        if verified is None:
            continue
        recipe = verified.recipe
        kind = str(recipe.get("kind", ""))
        try:
            if kind == "patch":
                sites: List[PatchSite] = []
                patterns: List[str] = []
                lengths: List[int] = []
                for locator in recipe.get("locators", []):
                    address, pattern = _recipe_locator(image, locator, label)
                    original = _recipe_bytes(locator.get("originalHex"), "原字节")
                    patched = _recipe_bytes(locator.get("patchedHex"), "补丁字节")
                    if len(original) != len(patched):
                        raise ProfileError("%s证据补丁长度不一致" % label)
                    if image.read_va(address, len(original)) != original:
                        raise ProfileError("%s证据原字节不匹配" % label)
                    instruction_length = _recipe_int(
                        locator.get("instructionLength"), len(original))
                    if instruction_length != len(original):
                        raise ProfileError("%s证据没有覆盖完整指令" % label)
                    sites.append(PatchSite(address, original, patched))
                    patterns.append(pattern)
                    lengths.append(instruction_length)
                if not sites:
                    raise ProfileError("%s证据没有补丁站点" % label)
                spec = PatchSpec(
                    key, label, tuple(sites), tuple(patterns),
                    str(recipe.get("normalizedFingerprint", "")), tuple(lengths),
                    str(recipe.get("rollbackRule", "owned-bytes-only")))
                patches[key] = spec
            elif kind == "dynamic-stub":
                call_sites: List[DynamicCallSite] = []
                patterns = []
                for locator in recipe.get("callLocators", []):
                    address, pattern = _recipe_locator(image, locator, label)
                    original = _recipe_bytes(locator.get("originalHex"), "调用点原字节")
                    length = _recipe_int(locator.get("instructionLength"),
                                         len(original))
                    if len(original) != length or length < 5:
                        raise ProfileError("%s调用点没有覆盖完整 rel32 指令" % label)
                    if image.read_va(address, length) != original:
                        raise ProfileError("%s调用点原字节不匹配" % label)
                    call_sites.append(DynamicCallSite(
                        address, original, length,
                        (_recipe_int(locator.get("branchOpcodeHex"))
                         if isinstance(locator.get("branchOpcodeHex"), int)
                         else int(str(locator.get("branchOpcodeHex", "E9")), 16)),
                        _recipe_int(locator.get("stubOffset"), 0),
                        bool(locator.get("operandOnly", False))))
                    patterns.append(pattern)
                relocations = tuple(StubRelocation(
                    _recipe_int(item["offset"]), str(item["kind"]),
                    _recipe_int(item["value"]), _recipe_int(item.get("addend"), 0))
                    for item in recipe.get("relocations", []))
                dynamic_patches[key] = DynamicPatchSpec(
                    key, label, tuple(call_sites),
                    _recipe_bytes(recipe.get("stubTemplateHex"), "stub模板"),
                    relocations, tuple(patterns),
                    str(recipe.get("normalizedFingerprint", "")),
                    str(recipe.get("rollbackRule",
                                   "owned-branches-and-no-eip-in-stub")))
            elif kind == "remote-call":
                locator = dict(recipe.get("locator", {}))
                address, pattern = _recipe_locator(image, locator, label)
                signature = _recipe_bytes(locator.get("prologueHex"), "函数入口字节")
                if image.read_va(address, len(signature)) != signature:
                    raise ProfileError("%s函数入口原字节不匹配" % label)
                expected_wrapper = {
                    "turn_refresh_direction": "legacy-turn-v1",
                    "turn_refresh_position": "legacy-position-v1",
                }.get(key, "")
                if expected_wrapper and recipe.get("wrapperKind") != expected_wrapper:
                    raise ProfileError("%s调用包装尚未由扳手实现" % label)
                remote_calls[key] = RemoteCallSpec(
                    key, label, address, signature, True, pattern,
                    str(recipe.get("normalizedFingerprint", "")),
                    str(recipe.get("callingConvention", "unknown")),
                    str(recipe.get("ecxSource", "")),
                    tuple(str(item) for item in recipe.get("arguments", [])),
                    _recipe_int(recipe.get("calleeCleanup"), 0),
                    tuple(str(item) for item in recipe.get("preconditions", [])),
                    tuple(str(item) for item in recipe.get("postconditions", [])),
                    _recipe_int(recipe.get("contextReference"), 0),
                    str(recipe.get("wrapperKind", "")))
            elif kind == "item-mapping":
                locator = dict(recipe.get("locator", {}))
                anchor, _pattern = _recipe_locator(image, locator, label)
                operand_offset = _recipe_int(locator.get("operandOffset"), 0)
                base = struct.unpack("<I", image.read_va(anchor + operand_offset, 4))[0]
                id_min = _recipe_int(recipe.get("idMin"), -1)
                id_max = _recipe_int(recipe.get("idMax"), -1)
                width = _recipe_int(recipe.get("width"), 0)
                stride = _recipe_int(recipe.get("stride"), 0)
                if not (0 <= id_min <= id_max < limits["item_count"]):
                    raise ProfileError("消耗品证据 ID 范围无效")
                if width not in (1, 2, 4) or stride < width:
                    raise ProfileError("消耗品证据计数宽度或步长无效")
                item_ids = [_recipe_int(item) for item in recipe.get("itemIds", [])]
                if (len(set(item_ids)) != len(item_ids) or
                        any(item < id_min or item > id_max for item in item_ids)):
                    raise ProfileError("消耗品证据显式 ID 无效或重复")
                category_pairs = [list(item) for item in recipe.get("categoryPairs", [])]
                if any(len(item) != 2 or any(
                        not 0 <= _recipe_int(value) <= 255 for value in item)
                       for item in category_pairs):
                    raise ProfileError("消耗品证据类别矩阵无效")
                category_pairs = [[_recipe_int(value) for value in item]
                                  for item in category_pairs]
                addresses["consumable_counts"] = base
                metadata["consumable_mapping"] = {
                    "idMin": id_min, "idMax": id_max, "width": width,
                    "stride": stride,
                    "baseDereference": bool(recipe.get("baseDereference", False)),
                    "itemIds": item_ids,
                    "categoryPairs": category_pairs,
                }
            else:
                raise ProfileError("%s证据配方类型不受支持: %s" % (label, kind))
            capabilities[key] = _capability(key, True, recipe=recipe)
        except (KeyError, TypeError, ValueError, ProfileError) as exc:
            capabilities[key] = capabilities[key].with_state(
                CapabilityState.UNAVAILABLE,
                reason="%s证据配方无法应用: %s" % (label, exc),
                reason_code="EVIDENCE_RECIPE_REJECTED")


def detect_engine(exe_path: str, version_part: Optional[int] = None) -> EngineProfile:
    image = PEImage(exe_path)
    if not image.is_x86:
        raise ProfileError("目标 Ekd5.exe 不是 32 位 x86 程序")
    sha = image.sha256
    known = KNOWN_66.get(sha)
    if known and os.path.getsize(exe_path) != known[1]:
        raise ProfileError("已知基底的文件长度与 SHA 身份不一致")
    if not known and version_part != 6:
        raise ProfileError("目标不是已知 6.6，且版本资源低位不是 6")

    variant = known[0] if known else "未知 6.6 派生版"
    addresses = {
        "battle_units": 0x004A7B20,
        "person_pointer": 0x004CEA00,
        "person_r": 0x0050F800,
        "person_s": 0x00501000,
        "person_face": 0x0050F000,
        "merit": 0x00508000,
        "warehouse": 0x004B0783,
        "money": 0x004B077C,
        "alignment": 0x004B0782,
        "merit_pool": 0x00505F40,
        "save_state": 0x004B0770,
        "battle_state": 0x004B3D08,
        "battle_sp": 0x00501C00,
        "job_names": 0x005000D0,
        "item_table": 0x004A1140,
        "effect_names": 0x004CC600,
        "effect_assign_pointer": 0x00500C3B,
        "effect_assign": 0,
        "exclusive_set": 0x0050E000,
        "fatal_pointer": 0x00500C37,
        "bool_vars": 0x00492FC8,
        "int_vars": 0x00502000,
        "ptr_vars": 0x00506000,
        "consumable_counts": 0,
    }
    limits = {
        "battle_ours": 20,
        "battle_friends": 40,
        "battle_enemies": 190,
        "battle_stride": 0x30,
        "person_count": 1024,
        "person_stride": 0x48,
        "merit_count": 102,
        "warehouse_count": 200,
        "item_count": ITEM_RECORD_COUNT_66,
        "item_record_count": ITEM_RECORD_COUNT_66,
        "equipment_count": EQUIPMENT_COUNT_66,
        "item_stride": 0x19,
        "item_name_size": 15,
        "effect_count": 255,
        "effect_stride": EFFECT_ROW_SIZE_66,
        "effect_character_slots": EFFECT_CHARACTER_SLOTS_66,
        "effect_job_slots": EFFECT_JOB_SLOTS_66,
        "effect_value_per_slot": True,
        "effect_job_count": EFFECT_JOB_COUNT_66,
        "fatal_count": 80,
        "fatal_stride": 16,
        "variable_count": 4096,
    }

    capabilities: Dict[str, FeatureCapability] = {}
    patches: Dict[str, PatchSpec] = {}
    dynamic_patches: Dict[str, DynamicPatchSpec] = {}
    metadata: Dict[str, object] = {
        "item_layout": {
            "lowFile": "Data.e5", "lowOffset": ITEM_LOW_OFFSET_66,
            "lowCount": ITEM_LOW_COUNT_66,
            "highFile": "Star.e5", "highOffset": ITEM_HIGH_OFFSET_66,
            "highCount": ITEM_HIGH_COUNT_66,
            "rowSize": ITEM_ROW_SIZE_66,
        },
        "consumable_item_ids": list(range(
            CONSUMABLE_ID_MIN_66, CONSUMABLE_ID_MAX_66 + 1)),
        "effect_empty_character": EFFECT_EMPTY_CHARACTER_66,
        "auto_return_layout": {},
        "variable_layouts": {
            "variables_bool": {
                "addressKey": "bool_vars", "countOffset": None,
                "dataOffset": 0, "stride": 1, "width": 1,
                "signed": False, "storage": "bitset",
                "bitOrder": "msb0", "storageBytes": 512,
            },
            "variables_int": {
                "addressKey": "int_vars", "countOffset": None,
                "dataOffset": 0, "stride": 4, "width": 4,
                "signed": True,
            },
            "variables_ptr": {
                "addressKey": "ptr_vars", "countOffset": None,
                "dataOffset": 0, "stride": 4, "width": 4,
                "signed": True,
            },
        },
    }
    auto_patch, auto_contract, auto_reason = locate_auto_return_patch_66(image)
    if auto_patch is not None:
        patches[auto_patch.key] = auto_patch
        metadata["auto_return_layout"].update(auto_contract)
    consumable_base, consumable_mapping, consumable_reason = (
        locate_consumable_mapping_66(image))
    if consumable_base is not None:
        addresses["consumable_counts"] = consumable_base
        metadata["consumable_mapping"] = consumable_mapping
    item_metadata_reason = ""
    try:
        metadata["item_table_66"] = load_item_table_66(exe_path)
        item_metadata_ok = True
    except ProfileError as exc:
        item_metadata_ok = False
        item_metadata_reason = str(exc)
    for key, label in (
        ("control_all_factions", "不分敌我"),
        ("control_friendly", "敌友军可控"),
        ("control_no_ai", "禁止AI"),
        ("control_move_after_wait", "待命后移动"),
        ("control_move_255", "移动力255"),
        ("control_pass_through", "穿越移动"),
    ):
        patch, reason = _locate_patch(image, key, label)
        capabilities[key] = _capability(
            key, patch is not None, reason,
            recipe=patch.recipe() if patch is not None else None)
        if patch:
            patches[key] = patch

    # These structure/function signatures are deliberately independent of SHA.
    # The third tuple member is the operand offset. -4 means the final four
    # bytes of the signature; None means the signature identifies a function.
    structural = {
        "battle": (
            "55 8B EC 0F B6 C9 6B C9 30 81 C1 ?? ?? ?? ?? 5D C3", 11),
        "person": (
            "55 8B EC 0F B7 4D 08 6B C9 48 03 0D ?? ?? ?? ?? 5D C2 04 00", 12),
        "person_r": (
            "55 8B EC 51 E8 ?? ?? ?? ?? 0F B7 04 45 ?? ?? ?? ?? 59 5D C3", 13),
        "person_s": (
            "68 00 00 03 00 68 ?? ?? ?? ?? 8D 4D F8 E8 ?? ?? ?? ?? 01 45 FC", 6),
        "person_face": (
            "55 8B EC E8 ?? ?? ?? ?? 0F B7 04 45 ?? ?? ?? ?? 85 C0 74 03 83 C0 07", 12),
        "fatal": (
            "55 8B EC 83 EC 0C 54 6A 02 6A 04 FF 75 08 E8 ?? ?? ?? ?? 0F B6 45 F4 3C 50 73 25 6B C8 10 03 0D ?? ?? ?? ?? 8A 45 F6 6B D0 03 03 CA 8B 55 FA 3C 05", 32),
        "recalculate": (
            "55 8B EC FF 71 1B FF 71 1F FF 35 F8 5F 50 00 33 D2 3B 4D 08", None),
        "revive": (
            "55 8B EC 6A 00 83 EC 34 8B 4D 08 E8 ?? ?? ?? ?? 85 C0 75 11 81 F9 00 04 00 00", None),
        "weather": (
            "55 8B EC 51 0F B6 51 11 6B C2 06 8A 55 08 8A 94 10 00 E1 48 00", None),
        "effect": (
            "55 8B EC 51 E8 ?? ?? ?? ?? 50 81 65 08 FF 00 00 00 FF 75 FC FF 75 10 FF 75 08 8B 15 ?? ?? ?? ?? E8 ?? ?? ?? ?? 50 FF 75 10", 28),
        "effect_query_layout": (
            "55 8B EC 8B 4D 08 C1 E1 04 03 D1 52 6A 00 6A 00 8B 55 F8 83 FA 04 73 16 6B D2 03 03 55 FC 66 3B 02 74 05 FF 45 F8 EB E8 0F B6 52 02 EB 02 33 D2 52 50 FF 75 08 E8 ?? ?? ?? ?? 8B 55 F0 8B 4D 0C E8 ?? ?? ?? ?? 89 45 F0 8B 4D 10 E8 ?? ?? ?? ?? 50 8B 45 F4 3C 02 73 25 D1 E0 83 C0 0C", None),
        "variables_bool_anchor": (
            "5D C2 0C 00 55 8B EC 68 ?? ?? ?? ?? FF 75 0C FF 45 08 FF 75 08 8B 4D FC", 8),
        "variables_bool_storage": (
            "55 8B EC 0F B7 45 08 C1 F8 03 50 0F B7 45 08 99 33 C2 "
            "83 E0 07 33 C2 85 C0 74 03 FF 45 FC 58 5D C2 04 00", None),
        "turn_refresh_direction": (
            "55 8B EC 6A 00 6A 00 83 EC 10 8B 4D 08 E8 ?? ?? ?? ?? 85 C0 74 04 8B C8", None),
    }
    located: Dict[str, int] = {}
    extracted: Dict[str, int] = {}
    for key, (pattern, operand_offset) in structural.items():
        signature = MaskedSignature.parse(pattern)
        hits = image.find_signature(signature)
        if len(hits) == 1:
            located[key] = hits[0]
            details = {"signature": hits[0]}
            if operand_offset is not None:
                if operand_offset < 0:
                    operand_offset = len(signature.pattern) + operand_offset
                operand = struct.unpack("<I", image.read_va(
                    hits[0] + operand_offset, 4))[0]
                extracted[key] = operand
                details["operand"] = operand
            capabilities[key] = _capability(
                key, True,
                recipe={
                    "kind": "masked-signature",
                    "pattern": pattern,
                    "operandOffset": operand_offset,
                }, **details)
        else:
            capabilities[key] = _capability(
                key, False, "%s结构签名匹配数为 %d" % (key, len(hits)))

    if capabilities["battle"].statically_verified:
        addresses["battle_units"] = extracted["battle"]
    if capabilities["person"].statically_verified:
        addresses["person_pointer"] = extracted["person"]
    if capabilities["person_r"].statically_verified:
        addresses["person_r"] = extracted["person_r"]
    if capabilities["person_s"].statically_verified:
        addresses["person_s"] = extracted["person_s"]
    if capabilities["person_face"].statically_verified:
        addresses["person_face"] = extracted["person_face"]
    if capabilities["fatal"].statically_verified:
        addresses["fatal_pointer"] = extracted["fatal"]
    effect_layout_ok = all(capabilities[key].statically_verified for key in
                           ("effect", "effect_query_layout"))
    if effect_layout_ok:
        addresses["effect_assign_pointer"] = extracted["effect"]
        capabilities["effect"] = _capability(
            "effect", True,
            recipe={
                "kind": "effect-assignment-66",
                "pointerPattern": structural["effect"][0],
                "layoutPattern": structural["effect_query_layout"][0],
                "pointerAddress": extracted["effect"],
                "rowSize": limits["effect_stride"],
                "characterSlots": limits["effect_character_slots"],
                "jobSlots": limits["effect_job_slots"],
                "valuePerSlot": True,
            },
            pointer=extracted["effect"],
            query=located["effect_query_layout"])
    else:
        capabilities["effect"] = _capability(
            "effect", False, "6.6特效分配指针或4角色2兵种布局签名未通过")
    bool_layout_ok = all(capabilities[key].statically_verified for key in
                         ("variables_bool_anchor", "variables_bool_storage"))
    if bool_layout_ok:
        addresses["bool_vars"] = extracted["variables_bool_anchor"] + 0x90

    person_tables_ok = all(capabilities[key].statically_verified for key in
                           ("person", "person_r", "person_s", "person_face"))
    merit_refs = image.find_literal_references(addresses["merit"])
    if len(merit_refs) != 2:
        person_tables_ok = False
    if not person_tables_ok:
        capabilities["person"] = _capability(
            "person", False, "人物数组、R/S/头像或功勋表签名未全部通过")

    shared_data_ok = all(capabilities[key].statically_verified
                         for key in ("battle", "person", "effect"))
    exclusive_refs = image.find_literal_references(addresses["exclusive_set"])
    if len(exclusive_refs) != 5:
        capabilities["effect"] = _capability(
            "effect", False, "专属/套装表引用数为 %d" % len(exclusive_refs))
        shared_data_ok = False
    warehouse_refs_ok = all(image.find_literal_references(addresses[key])
                            for key in ("warehouse", "money", "merit_pool"))
    warehouse_refs_ok = (warehouse_refs_ok and
                         addresses["alignment"] == addresses["money"] + 6)
    capabilities["warehouse"] = _capability(
        "warehouse", shared_data_ok and warehouse_refs_ok,
        "仓库或基础表结构签名未通过"
        if not (shared_data_ok and warehouse_refs_ok) else "",
        recipe={
            "kind": "runtime-tables",
            "battleStride": limits["battle_stride"],
            "itemStride": limits["item_stride"],
            "warehouseStride": 3,
            "warehouseRefs": bool(warehouse_refs_ok),
        })
    capabilities["item_metadata"] = _capability(
        "item_metadata", item_metadata_ok,
        item_metadata_reason if not item_metadata_ok else "",
        recipe={
            "kind": "split-file-item-table",
            "lowFile": "Data.e5", "lowOffset": ITEM_LOW_OFFSET_66,
            "lowCount": ITEM_LOW_COUNT_66,
            "highFile": "Star.e5", "highOffset": ITEM_HIGH_OFFSET_66,
            "highCount": ITEM_HIGH_COUNT_66,
            "rowSize": ITEM_ROW_SIZE_66,
            "nameSize": 0x0F,
        })
    variable_results = {}
    for address_key, capability_key in (
            ("bool_vars", "variables_bool"),
            ("int_vars", "variables_int"),
            ("ptr_vars", "variables_ptr")):
        if address_key == "bool_vars":
            available = bool_layout_ok
        else:
            available = bool(image.find_literal_references(addresses[address_key]))
        variable_results[capability_key] = available
        capabilities[capability_key] = _capability(
            capability_key, available,
            "%s基址引用尚未通过" % address_key if not available else "",
            recipe={
                "kind": "variable-table", "addressKey": address_key,
                "count": limits["variable_count"],
                **metadata["variable_layouts"][capability_key],
            })
    variable_refs_ok = all(variable_results.values())
    capabilities["variables"] = _capability(
        "variables", variable_refs_ok,
        "变量基址引用尚未通过" if not variable_refs_ok else "",
        recipe={"kind": "variable-groups", "groups": 3,
                "count": limits["variable_count"]})
    capabilities["diy"] = _capability(
        "diy", True,
        recipe={"kind": "validated-custom-write", "widths": [1, 2, 4],
                "pageCheck": True, "readback": True})
    capabilities["item_bulk_treasure"] = _capability(
        "item_bulk_treasure",
        (capabilities["warehouse"].statically_verified and
         capabilities["item_metadata"].statically_verified),
        "6.6仓库或物品文件表语义探针未通过"
        if not (capabilities["warehouse"].statically_verified and
                capabilities["item_metadata"].statically_verified) else "",
        recipe={"kind": "treasure-filter", "rowStride": 0x19,
                 "catalogOffset": 0x18, "catalogValue": 1,
                "equipmentCount": limits["equipment_count"],
                 "warehouseCount": 200,
                 "itemSource": "Data.e5[0..103]+Star.e5[104..254]"})
    capabilities["item_consumables"] = _capability(
        "item_consumables", consumable_base is not None,
        consumable_reason if consumable_base is None else "",
        reason_code=("CONSUMABLE_SIGNATURE_MISMATCH"
                     if consumable_base is None else ""),
        recipe={
            "kind": "consumable-count-array",
            "countBase": consumable_base,
            **consumable_mapping,
        } if consumable_base is not None else None)
    capabilities["control_auto_return"] = _capability(
        "control_auto_return", auto_patch is not None,
        auto_reason,
        reason_code=("AUTO_RETURN_STATIC_NOT_LOCATED" if auto_reason else ""),
        recipe={
            **auto_patch.recipe(),
            "mode": auto_contract["mode"],
            "callSites": ["0x%08X" % value
                          for value in auto_contract["callSites"]],
            "nativeEffect": "0x%08X" % auto_contract["nativeEffect"],
            "patchSites": ["0x%08X" % value
                           for value in auto_contract["patchSites"]],
        } if auto_patch is not None else None)
    turn_located = capabilities["turn_refresh_direction"].statically_verified
    if turn_located:
        capabilities["turn_refresh_direction"] = _capability(
            "turn_refresh_direction", True,
            recipe={
                "kind": "remote-call",
                "address": located["turn_refresh_direction"],
                "callingConvention": "stdcall",
                "arguments": [
                    "data_id:u32", "sentinel:u32", "direction:u32",
                    "reserved:u32", "refresh:u32", "redraw:u32",
                ],
                "calleeCleanup": 24,
                "wrapperKind": "turn-66-six-args-v1",
            })
    capabilities["turn_refresh_position"] = _capability(
        "turn_refresh_position", False, "6.6坐标刷新ABI尚未动态验证",
        reason_code="POSITION_ABI_NOT_VERIFIED")

    remote_calls = {
        "recalculate": RemoteCallSpec(
            "recalculate", "人物能力重算", located.get("recalculate", 0x004075DF),
            b"\x55\x8B\xEC\xFF\x71\x1B", capabilities["recalculate"].runtime_verified,
            structural["recalculate"][0], capabilities["recalculate"].recipe_id,
            "thiscall", "ECX=人物记录", ("data_id:u16",), 0,
            ("人物指针有效",), ("人物派生能力已重算",)),
        "revive": RemoteCallSpec(
            "revive", "战场复活", located.get("revive", 0x004092C0),
            b"\x55\x8B\xEC\x6A\x00\x83\xEC\x34", capabilities["revive"].runtime_verified,
            structural["revive"][0], capabilities["revive"].recipe_id,
            "stdcall", "", ("direction:u32", "x:u32", "y:u32", "data_id:u32"),
            16, ("目标槽为空且坐标有效",), ("单位结构和地图占用已建立",)),
        "weather": RemoteCallSpec(
            "weather", "天气刷新", located.get("weather", 0x0041D9D1),
            b"\x55\x8B\xEC\x51", capabilities["weather"].runtime_verified,
            structural["weather"][0], capabilities["weather"].recipe_id,
            "thiscall", "ECX=天气上下文", ("weather:u8",), 0,
            ("天气值在有效范围",), ("天气状态和画面已刷新",)),
        "turn_refresh_direction": RemoteCallSpec(
            "turn_refresh_direction", "转向刷新",
            located.get("turn_refresh_direction", 0),
            b"\x55\x8B\xEC\x6A\x00\x6A\x00\x83" if turn_located else b"",
            turn_located,
            structural["turn_refresh_direction"][0],
            capabilities["turn_refresh_direction"].recipe_id,
            "stdcall", "",
            ("data_id:u32", "sentinel:u32", "direction:u32",
             "reserved:u32", "refresh:u32", "redraw:u32"),
            24, ("战场单位有效",), ("方向已立即刷新",), 0,
            "turn-66-six-args-v1"),
        "turn_refresh_position": RemoteCallSpec(
            "turn_refresh_position", "坐标刷新", 0, b"", False),
    }
    _materialize_verified_recipes(
        image, capabilities, patches, dynamic_patches, remote_calls,
        addresses, limits, metadata)
    return EngineProfile(
        6, "6.6", variant, sha, os.path.getsize(exe_path), image.image_base,
        image.size_of_image, addresses, limits, capabilities, patches, remote_calls,
        dynamic_patches=dynamic_patches, metadata=metadata,
        force_unverified_66=True)


def legacy_profile(version: int) -> EngineProfile:
    """Preserve the old 6.1-6.5 branches while using MemorySession."""
    names = {0: "6.4/5", 1: "6.3 MP+", 2: "6.3", 3: "6.2", 4: "6.1"}
    if version not in names:
        raise ProfileError("不支持的旧引擎版本")
    expanded = version == 0
    addresses = {
        "battle_units": 0x004A7B20 if expanded else 0x004B2C50,
        "person_pointer": 0x004CEA00,
        "person_r": 0x0050F800,
        "person_s": 0x00501000,
        "person_face": 0x0050F000,
        "merit": 0x00508000 if expanded else 0x00508400,
        "warehouse": 0x004B0783,
        "money": 0x004B077C,
        "alignment": 0x004B0782,
        "merit_pool": 0x00505F40,
        "save_state": 0x004B0770,
        "battle_state": 0x004B3D08,
        "battle_sp": 0x00501C00,
        "job_names": 0x005000D0,
        "item_table": 0x004A1140,
        "effect_assign": 0x00508998 if version == 0 else 0x005089B0,
        "exclusive_set": 0x0050E800 if version >= 3 else 0x0050E400,
        "fatal_table": 0x00511800 if expanded else 0x00508800,
        "bool_vars": 0x00492FC8,
        "int_vars": 0x00502000,
        "ptr_vars": 0x00506000,
    }
    limits = {
        "battle_ours": 20 if expanded else 16,
        "battle_friends": 40 if expanded else 19,
        "battle_enemies": 190 if expanded else 80,
        "battle_stride": 0x30 if expanded else 0x24,
        "person_count": 1024,
        "person_stride": 0x48,
        "merit_count": 102,
        "warehouse_count": 200,
        "item_count": 255 if expanded else 154,
        "item_stride": 0x19,
        "item_name_size": 12,
        "effect_count": 180 if expanded else 144,
        "effect_stride": 8,
        "effect_character_slots": 3,
        "effect_job_slots": 1,
        "effect_value_per_slot": False,
        "effect_job_count": 80,
        "fatal_count": 80 if expanded else 36,
        "fatal_stride": 16,
        "variable_count": 4096,
    }
    legacy_keys = (
        "battle", "person", "warehouse", "variables", "variables_bool",
        "variables_int", "variables_ptr", "diy", "fatal",
        "effect", "recalculate", "revive", "weather",
        "turn_refresh_direction", "turn_refresh_position",
        "item_bulk_treasure", "item_consumables", "control_friendly",
        "control_all_factions", "control_no_ai", "control_move_after_wait",
        "control_move_255", "control_pass_through", "control_auto_return")
    capabilities = {
        key: FeatureCapability(
            key, CapabilityState.ENABLED, recipe_id="legacy.%d.%s" % (version, key))
        for key in legacy_keys
    }
    revive_address = 0x004092C7 if expanded else 0x004092E0
    if version == 4:
        revive_address = 0x0040930F
    remote_calls = {
        "recalculate": RemoteCallSpec("recalculate", "人物能力重算",
                                      0x004075DF, b"", True),
        "revive": RemoteCallSpec("revive", "战场复活",
                                 revive_address, b"", True),
        "weather": RemoteCallSpec("weather", "天气刷新",
                                   0x0041D9D1, b"", True),
        "turn_refresh_direction": RemoteCallSpec(
            "turn_refresh_direction", "转向刷新", 0x00457428, b"", True,
            calling_convention="thiscall", ecx_source="DWORD[0x004B5DF0]",
            arguments=("direction:u32", "data_id:u32", "flags:u32"),
            context_reference=0x004B5DF0, wrapper_kind="legacy-turn-v1"),
        "turn_refresh_position": RemoteCallSpec(
            "turn_refresh_position", "坐标刷新", 0x004594DD, b"", True,
            calling_convention="thiscall", ecx_source="DWORD[0x004B5DF0]",
            arguments=("direction:u32", "y:u32", "x:u32", "data_id:u32"),
            context_reference=0x004B5DF0, wrapper_kind="legacy-position-v1"),
    }
    metadata = {
        "variable_layouts": {
            key: {
                "addressKey": address_key, "countOffset": None,
                "dataOffset": 0, "stride": 4, "width": 4,
                "signed": True,
            }
            for key, address_key in (
                ("variables_bool", "bool_vars"),
                ("variables_int", "int_vars"),
                ("variables_ptr", "ptr_vars"),
            )
        },
    }
    return EngineProfile(version, names[version], "旧版兼容画像", "", 0,
                         REFERENCE_IMAGE_BASE, 0x200000, addresses, limits,
                         capabilities, {}, remote_calls, metadata=metadata)
