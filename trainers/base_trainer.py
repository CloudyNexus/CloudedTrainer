import logging

class BaseTrainer:
    """Base class for all game trainers"""
    
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.name = "Base Trainer"
        self.game_name = "Unknown Game"
        self.description = "Base trainer class"
        self.version = "1.0.0"
        self.process_name = "unknown"
        self.cheats = {}
        self.offsets = {}
        self.pointers = {}
        self.initialized = False
        self.logger = logging.getLogger(__name__)
    
    def initialize(self):
        """Initialize the trainer - must be implemented by subclasses"""
        self.initialized = True
        return True
    
    def update(self):
        """Update the trainer state - called periodically for active trainers"""
        pass
    
    def get_available_cheats(self):
        """Get a list of available cheats for this trainer"""
        return [
            {
                "id": cheat_id,
                "name": cheat_info.get("name", "Unknown"),
                "description": cheat_info.get("description", ""),
                "type": cheat_info.get("type", "toggle")
            }
            for cheat_id, cheat_info in self.cheats.items()
        ]
    
    def enable_cheat(self, cheat_id):
        """Enable a specific cheat"""
        if not self.initialized:
            return False
        
        if cheat_id not in self.cheats:
            return False
        
        cheat_info = self.cheats[cheat_id]
        handler = cheat_info.get("enable")
        
        if handler:
            return handler()
        return False
    
    def disable_cheat(self, cheat_id):
        """Disable a specific cheat"""
        if not self.initialized:
            return False
        
        if cheat_id not in self.cheats:
            return False
        
        cheat_info = self.cheats[cheat_id]
        handler = cheat_info.get("disable")
        
        if handler:
            return handler()
        return False
    
    def find_pattern(self, pattern, module_name=None):
        """Find a pattern in memory"""
        if not self.memory_manager:
            return None
        
        if module_name:
            # Get the module base address
            base_address = self.memory_manager.get_module_base(module_name)
            if not base_address:
                return None
            
            # Get memory maps for this module
            maps = self.memory_manager._get_memory_maps()
            for region in maps:
                if region["start"] == base_address:
                    # Scan only in this module's memory
                    return self.memory_manager.scan_pattern(pattern, region["start"], region["end"])
        
        # Scan all memory
        return self.memory_manager.scan_pattern(pattern)
    
    def read_value(self, address, data_type):
        """Read a value from memory"""
        if not self.memory_manager:
            return None
        
        return self.memory_manager.read_value(address, data_type)
    
    def write_value(self, address, value, data_type):
        """Write a value to memory"""
        if not self.memory_manager:
            return False
        
        return self.memory_manager.write_value(address, value, data_type)
    
    def read_pointer_chain(self, base_address, offsets, data_type):
        """Read a value from a pointer chain"""
        if not self.memory_manager:
            return None
        
        address = base_address
        
        # Follow the pointer chain
        for i, offset in enumerate(offsets):
            if i == len(offsets) - 1:
                # Last offset - read the value
                return self.read_value(address + offset, data_type)
            
            # Read the next address in the chain
            address_data = self.memory_manager.read_memory(address + offset, 8)  # Assuming 64-bit pointers
            if not address_data:
                return None
            
            # Update address for next iteration
            address = int.from_bytes(address_data, byteorder='little')
            if address == 0:
                return None
        
        return None
    
    def write_pointer_chain(self, base_address, offsets, value, data_type):
        """Write a value to a pointer chain"""
        if not self.memory_manager:
            return False
        
        address = base_address
        
        # Follow the pointer chain
        for i, offset in enumerate(offsets):
            if i == len(offsets) - 1:
                # Last offset - write the value
                return self.write_value(address + offset, value, data_type)
            
            # Read the next address in the chain
            address_data = self.memory_manager.read_memory(address + offset, 8)  # Assuming 64-bit pointers
            if not address_data:
                return False
            
            # Update address for next iteration
            address = int.from_bytes(address_data, byteorder='little')
            if address == 0:
                return False
        
        return False
