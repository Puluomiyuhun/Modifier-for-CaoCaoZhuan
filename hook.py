import sys 
from ctypes import *  


class my_hook:
    def life(self, h_process, dir, x, y, code ,add):
        PAGE_EXECUTE_READWRITE         = 0x00000040  
        VIRTUAL_MEM        =     ( 0x1000 | 0x2000 )
        kernel32      = windll.kernel32
        shellcode =  b''
        shellcode += b'\x55\x8B\xEC\x83\xEC\x10\x8B\x45\x08\x8B\x08\x8B\x50\x04\x89\x4D\xF0\x8B\x48\x08\x89\x55\xF8\x8B\x50\x0C\x8B\x40\x10\x89\x4D\xF4\x89\x55\xFC\x89\x45\x08\xFF\x75\xF0\xFF\x75\xF4\xFF\x75\xF8\xFF\x75\xFC\xFF\x55\x08\x33\xC0\x8B\xE5\x5D\xC2\x04\x00'
        code_size     = len(shellcode)  

        datacode =  b''
        datacode += self.intToBytes(dir,4)
        datacode += self.intToBytes(x,4)
        datacode += self.intToBytes(y,4)
        datacode += self.intToBytes(code,4)
        datacode += add
        #datacode += b'\x01\x00\x00\x00\x15\x00\x00\x00\x11\x00\x00\x00\x24\x00\x00\x00\xE0\x92\x40\x00'
        data_size     = len(datacode)

        h_process=int(h_process)

        arg_address = kernel32.VirtualAllocEx( h_process, 0, code_size, VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)
        print(arg_address)
        written = c_int(0)
        kernel32.WriteProcessMemory(h_process, arg_address, shellcode, code_size, byref(written))

        data_address = kernel32.VirtualAllocEx( h_process, 0, code_size, VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)
        print(data_address)
        written = c_int(0)
        kernel32.WriteProcessMemory(h_process, data_address, datacode, data_size, byref(written))  

        thread_id = c_ulong(0)  
        if not kernel32.CreateRemoteThread(h_process,None,0,arg_address,data_address,0,byref(thread_id)):
            sys.exit(0)
    
    def recal(self, h_process, code):
        PAGE_EXECUTE_READWRITE         = 0x00000040  
        VIRTUAL_MEM        =     ( 0x1000 | 0x2000 )
        kernel32      = windll.kernel32
        shellcode =  b''
        shellcode += b'\x55\x8B\xEC\x8B\x45\x08\x8B\x08\xFF\x30\xFF\x50\x04\x8B\xE5\x5D\xC2\x04\x00'
        code_size     = len(shellcode)  

        datacode =  b''
        datacode += self.intToBytes(code,4)
        datacode += b'\xDF\x75\x40\x00'
        data_size     = len(datacode)

        h_process=int(h_process)

        arg_address = kernel32.VirtualAllocEx( h_process, 0, code_size, VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)
        written = c_int(0)
        kernel32.WriteProcessMemory(h_process, arg_address, shellcode, code_size, byref(written))

        data_address = kernel32.VirtualAllocEx( h_process, 0, code_size, VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)
        written = c_int(0)
        kernel32.WriteProcessMemory(h_process, data_address, datacode, data_size, byref(written))  

        thread_id = c_ulong(0)  
        if not kernel32.CreateRemoteThread(h_process,None,0,arg_address,data_address,0,byref(thread_id)):
            sys.exit(0)

    def changeDir(self, h_process, dir, code):
        PAGE_EXECUTE_READWRITE         = 0x00000040  
        VIRTUAL_MEM        =     ( 0x1000 | 0x2000 )
        kernel32      = windll.kernel32
        shellcode =  b''
        shellcode += b'\x55\x8B\xEC\x8B\x45\x08\x6A\x00\xFF\x30\x68\xFF\xFF\x00\x00\xFF\x70\x04\x8B\x48\x08\xFF\x50\x0C\x8B\xE5\x5D\xC2\x04\x00'
        code_size     = len(shellcode)  

        datacode =  b''
        datacode += self.intToBytes(dir,4)
        datacode += self.intToBytes(code,4)
        datacode += b'\xF0\x5D\x4B\x00'
        datacode += b'\x28\x74\x45\x00'
        data_size     = len(datacode)

        h_process=int(h_process)

        arg_address = kernel32.VirtualAllocEx( h_process, 0, code_size, VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)
        written = c_int(0)
        kernel32.WriteProcessMemory(h_process, arg_address, shellcode, code_size, byref(written))

        data_address = kernel32.VirtualAllocEx( h_process, 0, code_size, VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)
        written = c_int(0)
        kernel32.WriteProcessMemory(h_process, data_address, datacode, data_size, byref(written))
        thread_id = c_ulong(0)  
        if not kernel32.CreateRemoteThread(h_process,None,0,arg_address,data_address,0,byref(thread_id)):
            sys.exit(0)

    def changePos(self, h_process, dir, x, y, code):
        PAGE_EXECUTE_READWRITE         = 0x00000040  
        VIRTUAL_MEM        =     ( 0x1000 | 0x2000 )
        kernel32      = windll.kernel32
        shellcode =  b''
        shellcode += b'\x55\x8B\xEC\x8B\x45\x08\xFF\x30\xFF\x70\x04\xFF\x70\x08\xFF\x70\x0C\x8B\x48\x10\xFF\x50\x14\x8B\xE5\x5D\xC2\x04\x00'
        code_size     = len(shellcode)  

        datacode =  b''
        datacode += self.intToBytes(dir,4)
        datacode += self.intToBytes(y,4)
        datacode += self.intToBytes(x,4)
        datacode += self.intToBytes(code,4)
        datacode += b'\xF0\x5D\x4B\x00'
        datacode += b'\xDD\x94\x45\x00'
        data_size     = len(datacode)

        h_process=int(h_process)

        arg_address = kernel32.VirtualAllocEx( h_process, 0, code_size, VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)
        written = c_int(0)
        kernel32.WriteProcessMemory(h_process, arg_address, shellcode, code_size, byref(written))

        data_address = kernel32.VirtualAllocEx( h_process, 0, code_size, VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)
        written = c_int(0)
        kernel32.WriteProcessMemory(h_process, data_address, datacode, data_size, byref(written))  

        thread_id = c_ulong(0)  
        if not kernel32.CreateRemoteThread(h_process,None,0,arg_address,data_address,0,byref(thread_id)):
            sys.exit(0)

    def changeWeather(self, h_process, weather):
        PAGE_EXECUTE_READWRITE         = 0x00000040  
        VIRTUAL_MEM        =     ( 0x1000 | 0x2000 )
        kernel32      = windll.kernel32
        shellcode =  b''
        #shellcode += b'\x55\x8B\xEC\x8B\x45\x08\xFF\x30\xFF\x50\x04\x8B\xE5\x5D\xC2\x04\x00'
        shellcode += b'\x55\x8B\xEC\x8B\x45\x08\xFF\x30\xB9\x08\x3D\x4B\x00\xFF\x50\x04\x8B\xE5\x5D\xC2\x04\x00'
        code_size     = len(shellcode)  

        datacode =  b''
        datacode += self.intToBytes(weather,4)
        #datacode += b'\xB0\x4A\x41\x00'
        datacode += b'\xD1\xD9\x41\x00'
        data_size     = len(datacode)

        h_process=int(h_process)

        arg_address = kernel32.VirtualAllocEx( h_process, 0, code_size, VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)
        written = c_int(0)
        kernel32.WriteProcessMemory(h_process, arg_address, shellcode, code_size, byref(written))
        data_address = kernel32.VirtualAllocEx( h_process, 0, code_size, VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)
        written = c_int(0)
        kernel32.WriteProcessMemory(h_process, data_address, datacode, data_size, byref(written))  

        thread_id = c_ulong(0)  
        if not kernel32.CreateRemoteThread(h_process,None,0,arg_address,data_address,0,byref(thread_id)):
            sys.exit(0)

    def intToBytes(self, value, length):
        result = []
        for i in range(0, length):
            result.append(value >> (i * 8) & 0xff)
        return bytes(result)