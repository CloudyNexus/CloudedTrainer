import os
import logging
import ctypes
import struct
import psutil
import time
import re

class MemoryManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.attached_pid = None
        self.process = None
        self.libc = ctypes.CDLL("libc.so.6")
        
        # Constants for ptrace
        self.PTRACE_ATTACH = 16
        self.PTRACE_DETACH = 17
        self.PTRACE_PEEKDATA = 2
        self.PTRACE_POKEDATA = 5
        
        # Define function signatures
        self.libc.ptrace.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
        self.libc.ptrace.restype = ctypes.c_long
    
    def attach(self, pid):
        """Attach to a process by PID"""
        if self.attached_pid:
            self.detach()
        
        try:
            # Check if process exists
            if not psutil.pid_exists(pid):
                self.logger.error(f"Process with PID {pid} does not exist")
                return False
            
            # Attach to the process
            result = self.libc.ptrace(self.PTRACE_ATTACH, pid, None, None)
            if result == -1:
                self.logger.error(f"Failed to attach to process {pid}. Make sure you have the necessary permissions.")
                return False
            
            # Wait for the process to stop
            os.waitpid(pid, 0)
            
            self.attached_pid = pid
            self.process = psutil.Process(pid)
            self.logger.info(f"Successfully attached to process {pid}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error attaching to process {pid}: {e}")
            return False
    
    def detach(self):
        """Detach from the currently attached process"""
        if not self.attached_pid:
            return True
        
        try:
            result = self.libc.ptrace(self.PTRACE_DETACH, self.attached_pid, None, None)
            if result == -1:
                self.logger.error(f"Failed to detach from process {self.attached_pid}")
                return False
            
            self.logger.info(f"Successfully detached from process {self.attached_pid}")
            self.attached_pid = None
            self.process = None
            return True
        
        except Exception as e:
            self.logger.error(f"Error detaching from process: {e}")
            return False
    
    def read_memory(self, address, size):
        """Read memory from the attached process"""
        if not self.attached_pid:
            self.logger.error("No process attached")
            return None
        
        try:
            data = b""
            aligned_address = address & ~(ctypes.sizeof(ctypes.c_long) - 1)
            
            # Read memory in chunks of long size
            long_size = ctypes.sizeof(ctypes.c_long)
            
            bytes_to_next_boundary = (aligned_address + long_size) - address
            first_chunk_size = min(bytes_to_next_boundary, size)
            
            # Read the first chunk that might be unaligned
            word = self.libc.ptrace(self.PTRACE_PEEKDATA, self.attached_pid, aligned_address, None)
            if word == -1:
                self.logger.error(f"Failed to read memory at address {hex(aligned_address)}")
                return None
            
            word_bytes = struct.pack("P", word)
            offset = address - aligned_address
            data += word_bytes[offset:offset + first_chunk_size]
            
            # Read remaining aligned chunks
            remaining_size = size - first_chunk_size
            current_address = aligned_address + long_size
            
            while remaining_size > 0:
                chunk_size = min(long_size, remaining_size)
                word = self.libc.ptrace(self.PTRACE_PEEKDATA, self.attached_pid, current_address, None)
                if word == -1:
                    self.logger.error(f"Failed to read memory at address {hex(current_address)}")
                    return None
                
                word_bytes = struct.pack("P", word)
                data += word_bytes[:chunk_size]
                
                current_address += long_size
                remaining_size -= chunk_size
            
            return data
        
        except Exception as e:
            self.logger.error(f"Error reading memory: {e}")
            return None
    
    def write_memory(self, address, data):
        """Write memory to the attached process"""
        if not self.attached_pid:
            self.logger.error("No process attached")
            return False
        
        try:
            aligned_address = address & ~(ctypes.sizeof(ctypes.c_long) - 1)
            long_size = ctypes.sizeof(ctypes.c_long)
            
            # Handle first potentially unaligned chunk
            if address != aligned_address or len(data) < long_size:
                # Read the current value to modify only the relevant bytes
                word = self.libc.ptrace(self.PTRACE_PEEKDATA, self.attached_pid, aligned_address, None)
                if word == -1:
                    self.logger.error(f"Failed to read memory at address {hex(aligned_address)}")
                    return False
                
                word_bytes = bytearray(struct.pack("P", word))
                offset = address - aligned_address
                first_chunk_size = min(len(data), long_size - offset)
                
                # Replace only the bytes we want to change
                for i in range(first_chunk_size):
                    word_bytes[offset + i] = data[i]
                
                # Write back the modified word
                word = struct.unpack("P", bytes(word_bytes))[0]
                result = self.libc.ptrace(self.PTRACE_POKEDATA, self.attached_pid, aligned_address, word)
                if result == -1:
                    self.logger.error(f"Failed to write memory at address {hex(aligned_address)}")
                    return False
                
                # Move to the next chunk
                data = data[first_chunk_size:]
                current_address = aligned_address + long_size
            else:
                current_address = address
            
            # Write remaining aligned chunks
            while data:
                if len(data) >= long_size:
                    # Full word write
                    word = struct.unpack("P", data[:long_size])[0]
                    result = self.libc.ptrace(self.PTRACE_POKEDATA, self.attached_pid, current_address, word)
                    if result == -1:
                        self.logger.error(f"Failed to write memory at address {hex(current_address)}")
                        return False
                    
                    data = data[long_size:]
                    current_address += long_size
                else:
                    # Partial word write (last chunk)
                    # Read the current value to modify only the relevant bytes
                    word = self.libc.ptrace(self.PTRACE_PEEKDATA, self.attached_pid, current_address, None)
                    if word == -1:
                        self.logger.error(f"Failed to read memory at address {hex(current_address)}")
                        return False
                    
                    word_bytes = bytearray(struct.pack("P", word))
                    for i in range(len(data)):
                        word_bytes[i] = data[i]
                    
                    # Write back the modified word
                    word = struct.unpack("P", bytes(word_bytes))[0]
                    result = self.libc.ptrace(self.PTRACE_POKEDATA, self.attached_pid, current_address, word)
                    if result == -1:
                        self.logger.error(f"Failed to write memory at address {hex(current_address)}")
                        return False
                    
                    data = b""
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error writing memory: {e}")
            return False
    
    def scan_pattern(self, pattern, start_address=None, end_address=None):
        """Scan memory for a specific pattern"""
        if not self.attached_pid:
            self.logger.error("No process attached")
            return []
        
        try:
            # Get memory maps if not provided
            if start_address is None or end_address is None:
                maps = self._get_memory_maps()
            else:
                maps = [{"start": start_address, "end": end_address}]
            
            # Compile regex pattern
            if isinstance(pattern, str):
                # Hex string pattern (e.g. "A1 ? ? ? ? C3")
                byte_pattern = bytearray()
                mask = bytearray()
                
                for part in pattern.split():
                    if part == "?":
                        byte_pattern.append(0)
                        mask.append(0)
                    else:
                        byte_pattern.append(int(part, 16))
                        mask.append(1)
                
                regex_pattern = b""
                for i in range(len(byte_pattern)):
                    if mask[i]:
                        regex_pattern += bytes([byte_pattern[i]])
                    else:
                        regex_pattern += b"."
                
                compiled_pattern = re.compile(regex_pattern)
            else:
                # Assume already a bytes object
                compiled_pattern = re.compile(re.escape(pattern))
            
            # Scan memory regions
            results = []
            for region in maps:
                # Skip regions that are too small
                if region["end"] - region["start"] < len(pattern):
                    continue
                
                # Read the memory region
                region_data = self.read_memory(region["start"], region["end"] - region["start"])
                if not region_data:
                    continue
                
                # Find all matches
                for match in compiled_pattern.finditer(region_data):
                    match_address = region["start"] + match.start()
                    results.append(match_address)
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error scanning memory: {e}")
            return []
    
    def _get_memory_maps(self):
        """Get memory maps of the attached process"""
        if not self.process:
            return []
        
        try:
            maps = []
            map_path = f"/proc/{self.attached_pid}/maps"
            
            with open(map_path, 'r') as f:
                for line in f:
                    # Parse memory maps line
                    parts = line.split()
                    if len(parts) < 6:
                        continue
                    
                    address_range = parts[0].split('-')
                    start = int(address_range[0], 16)
                    end = int(address_range[1], 16)
                    
                    # Check permissions (needs read access)
                    permissions = parts[1]
                    if 'r' not in permissions:
                        continue
                    
                    maps.append({
                        "start": start,
                        "end": end,
                        "permissions": permissions,
                        "offset": int(parts[2], 16),
                        "dev": parts[3],
                        "inode": int(parts[4]),
                        "pathname": parts[5] if len(parts) > 5 else ""
                    })
            
            return maps
        
        except Exception as e:
            self.logger.error(f"Error getting memory maps: {e}")
            return []
    
    def get_module_base(self, module_name):
        """Get the base address of a module in the attached process"""
        if not self.attached_pid:
            return None
        
        try:
            maps = self._get_memory_maps()
            
            for region in maps:
                pathname = region.get("pathname", "")
                if module_name in pathname and region["permissions"][2] == 'x':  # Executable
                    return region["start"]
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error getting module base: {e}")
            return None
    
    def read_value(self, address, data_type):
        """Read a specific data type from memory"""
        type_sizes = {
            "int8": 1,
            "uint8": 1,
            "int16": 2,
            "uint16": 2,
            "int32": 4,
            "uint32": 4,
            "int64": 8,
            "uint64": 8,
            "float": 4,
            "double": 8
        }
        
        type_formats = {
            "int8": "b",
            "uint8": "B",
            "int16": "h",
            "uint16": "H",
            "int32": "i",
            "uint32": "I",
            "int64": "q",
            "uint64": "Q",
            "float": "f",
            "double": "d"
        }
        
        if data_type not in type_sizes:
            self.logger.error(f"Unsupported data type: {data_type}")
            return None
        
        size = type_sizes[data_type]
        fmt = type_formats[data_type]
        
        data = self.read_memory(address, size)
        if not data:
            return None
        
        try:
            value = struct.unpack(fmt, data)[0]
            return value
        except struct.error:
            self.logger.error(f"Error unpacking data type {data_type} at address {hex(address)}")
            return None
    
    def write_value(self, address, value, data_type):
        """Write a specific data type to memory"""
        type_formats = {
            "int8": "b",
            "uint8": "B",
            "int16": "h",
            "uint16": "H",
            "int32": "i",
            "uint32": "I",
            "int64": "q",
            "uint64": "Q",
            "float": "f",
            "double": "d"
        }
        
        if data_type not in type_formats:
            self.logger.error(f"Unsupported data type: {data_type}")
            return False
        
        fmt = type_formats[data_type]
        
        try:
            data = struct.pack(fmt, value)
            return self.write_memory(address, data)
        except struct.error:
            self.logger.error(f"Error packing data type {data_type} with value {value}")
            return False
