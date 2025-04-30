import logging
from trainers.base_trainer import BaseTrainer

class TF2Trainer(BaseTrainer):
    """Trainer for Team Fortress 2"""
    
    def __init__(self, memory_manager):
        super().__init__(memory_manager)
        self.name = "TF2 Trainer"
        self.game_name = "Team Fortress 2"
        self.description = "Trainer for Team Fortress 2"
        self.version = "1.0.0"
        self.process_name = "hl2_linux"
        
        # Define cheats
        self.cheats = {
            "infinite_health": {
                "name": "Infinite Health",
                "description": "Never lose health",
                "type": "toggle",
                "enable": self.enable_infinite_health,
                "disable": self.disable_infinite_health
            },
            "infinite_ammo": {
                "name": "Infinite Ammo",
                "description": "Never run out of ammunition",
                "type": "toggle",
                "enable": self.enable_infinite_ammo,
                "disable": self.disable_infinite_ammo
            },
            "speedhack": {
                "name": "Speed Hack",
                "description": "Move faster",
                "type": "toggle",
                "enable": self.enable_speedhack,
                "disable": self.disable_speedhack
            },
            "no_recoil": {
                "name": "No Recoil",
                "description": "Eliminate weapon recoil",
                "type": "toggle",
                "enable": self.enable_no_recoil,
                "disable": self.disable_no_recoil
            },
            "esp": {
                "name": "ESP",
                "description": "See enemies through walls",
                "type": "toggle",
                "enable": self.enable_esp,
                "disable": self.disable_esp
            }
        }
        
        # Game-specific variables
        self.logger = logging.getLogger(__name__)
        self.client_module = None
        self.engine_module = None
        self.local_player = None
        
        # Offsets (examples, would need to be updated for each game version)
        self.health_offset = 0xA8
        self.ammo_offset = 0x2B20
        self.speed_offset = 0xE8
        self.recoil_offset = 0x9B8
        
        # Original values for restoration
        self.original_speed = None
        
        # Active state tracking
        self.infinite_health_active = False
        self.infinite_ammo_active = False
        self.speedhack_active = False
        self.no_recoil_active = False
        self.esp_active = False
    
    def initialize(self):
        """Initialize the trainer"""
        if not self.memory_manager:
            self.logger.error("Memory manager not set")
            return False
        
        try:
            # Find module base addresses
            self.client_module = self.memory_manager.get_module_base("client.so")
            self.engine_module = self.memory_manager.get_module_base("engine.so")
            
            if not self.client_module or not self.engine_module:
                self.logger.error("Failed to find game modules")
                return False
            
            # Find local player
            local_player_offset = 0x6DD14C  # Example offset
            self.local_player = self.memory_manager.read_value(self.client_module + local_player_offset, "uint32")
            
            if not self.local_player:
                self.logger.error("Failed to find local player")
                return False
            
            self.initialized = True
            self.logger.info("TF2 trainer initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Error initializing TF2 trainer: {e}")
            return False
    
    def update(self):
        """Update the trainer state"""
        if not self.initialized:
            return
        
        try:
            # Update health if infinite health is active
            if self.infinite_health_active:
                self._update_health()
            
            # Update ammo if infinite ammo is active
            if self.infinite_ammo_active:
                self._update_ammo()
            
            # Update ESP if active
            if self.esp_active:
                self._update_esp()
        
        except Exception as e:
            self.logger.error(f"Error updating TF2 trainer: {e}")
    
    def enable_infinite_health(self):
        """Enable infinite health"""
        if not self.initialized:
            return False
        
        try:
            self.infinite_health_active = True
            self.logger.info("Infinite health enabled")
            return True
        
        except Exception as e:
            self.logger.error(f"Error enabling infinite health: {e}")
            return False
    
    def disable_infinite_health(self):
        """Disable infinite health"""
        if not self.initialized:
            return False
        
        try:
            self.infinite_health_active = False
            self.logger.info("Infinite health disabled")
            return True
        
        except Exception as e:
            self.logger.error(f"Error disabling infinite health: {e}")
            return False
    
    def enable_infinite_ammo(self):
        """Enable infinite ammo"""
        if not self.initialized:
            return False
        
        try:
            self.infinite_ammo_active = True
            self.logger.info("Infinite ammo enabled")
            return True
        
        except Exception as e:
            self.logger.error(f"Error enabling infinite ammo: {e}")
            return False
    
    def disable_infinite_ammo(self):
        """Disable infinite ammo"""
        if not self.initialized:
            return False
        
        try:
            self.infinite_ammo_active = False
            self.logger.info("Infinite ammo disabled")
            return True
        
        except Exception as e:
            self.logger.error(f"Error disabling infinite ammo: {e}")
            return False
    
    def enable_speedhack(self):
        """Enable speed hack"""
        if not self.initialized:
            return False
        
        try:
            # Store original speed
            self.original_speed = self.read_value(self.local_player + self.speed_offset, "float")
            
            # Set increased speed
            new_speed = self.original_speed * 2 if self.original_speed else 600.0
            self.write_value(self.local_player + self.speed_offset, new_speed, "float")
            
            self.speedhack_active = True
            self.logger.info("Speed hack enabled")
            return True
        
        except Exception as e:
            self.logger.error(f"Error enabling speed hack: {e}")
            return False
    
    def disable_speedhack(self):
        """Disable speed hack"""
        if not self.initialized:
            return False
        
        try:
            # Restore original speed
            if self.original_speed:
                self.write_value(self.local_player + self.speed_offset, self.original_speed, "float")
            
            self.speedhack_active = False
            self.logger.info("Speed hack disabled")
            return True
        
        except Exception as e:
            self.logger.error(f"Error disabling speed hack: {e}")
            return False
    
    def enable_no_recoil(self):
        """Enable no recoil"""
        if not self.initialized:
            return False
        
        try:
            # Set recoil to 0
            self.write_value(self.local_player + self.recoil_offset, 0.0, "float")
            self.write_value(self.local_player + self.recoil_offset + 4, 0.0, "float")
            
            self.no_recoil_active = True
            self.logger.info("No recoil enabled")
            return True
        
        except Exception as e:
            self.logger.error(f"Error enabling no recoil: {e}")
            return False
    
    def disable_no_recoil(self):
        """Disable no recoil"""
        if not self.initialized:
            return False
        
        try:
            self.no_recoil_active = False
            self.logger.info("No recoil disabled")
            return True
        
        except Exception as e:
            self.logger.error(f"Error disabling no recoil: {e}")
            return False
    
    def enable_esp(self):
        """Enable ESP"""
        if not self.initialized:
            return False
        
        try:
            self.esp_active = True
            self.logger.info("ESP enabled")
            return True
        
        except Exception as e:
            self.logger.error(f"Error enabling ESP: {e}")
            return False
    
    def disable_esp(self):
        """Disable ESP"""
        if not self.initialized:
            return False
        
        try:
            self.esp_active = False
            self.logger.info("ESP disabled")
            return True
        
        except Exception as e:
            self.logger.error(f"Error disabling ESP: {e}")
            return False
    
    def _update_health(self):
        """Update health value for infinite health"""
        try:
            # Get maximum health
            max_health_offset = 0xAC  # Example offset
            max_health = self.read_value(self.local_player + max_health_offset, "int32")
            
            if not max_health or max_health <= 0:
                max_health = 125  # Default max health
            
            # Set current health to maximum
            current_health = self.read_value(self.local_player + self.health_offset, "int32")
            
            if current_health < max_health:
                self.write_value(self.local_player + self.health_offset, max_health, "int32")
        
        except Exception as e:
            self.logger.error(f"Error updating health: {e}")
    
    def _update_ammo(self):
        """Update ammo values for infinite ammo"""
        try:
            # Get current weapon
            active_weapon_offset = 0xB10  # Example offset
            active_weapon = self.read_value(self.local_player + active_weapon_offset, "uint32")
            
            if not active_weapon:
                return
            
            # Get clip size
            clip_size_offset = 0x1790  # Example offset
            max_clip = self.read_value(active_weapon + clip_size_offset, "int32")
            
            if not max_clip or max_clip <= 0:
                return
            
            # Set current clip to maximum
            current_clip_offset = 0x1648  # Example offset
            current_clip = self.read_value(active_weapon + current_clip_offset, "int32")
            
            if current_clip < max_clip:
                self.write_value(active_weapon + current_clip_offset, max_clip, "int32")
            
            # Set reserve ammo to maximum as well
            reserve_ammo_offset = 0x164C  # Example offset
            self.write_value(active_weapon + reserve_ammo_offset, 999, "int32")
        
        except Exception as e:
            self.logger.error(f"Error updating ammo: {e}")
    
    def _update_esp(self):
        """Update ESP for seeing enemies through walls"""
        try:
            # Get maximum number of entities
            max_entities = 64  # Common value for TF2
            
            # Get entity list base
            entity_list_offset = 0x4DB09D8  # Example offset
            
            # Get local player team
            team_offset = 0xB68  # Example offset
            local_team = self.read_value(self.local_player + team_offset, "int32")
            
            if not local_team:
                return
            
            # Loop through all possible entities
            for i in range(max_entities):
                # Get entity from list
                entity_ptr = self.read_value(self.client_module + entity_list_offset + i * 4, "uint32")
                
                if not entity_ptr or entity_ptr == self.local_player:
                    continue
                
                # Check if entity is a player
                entity_team = self.read_value(entity_ptr + team_offset, "int32")
                
                if not entity_team or entity_team == local_team:
                    continue
                
                # Make entity glow through walls
                glow_offset = 0x1740  # Example offset
                self.write_value(entity_ptr + glow_offset, 1, "int8")
                
                # Set glow color (red for enemies)
                glow_r_offset = 0x1744  # Example offset
                glow_g_offset = 0x1748  # Example offset
                glow_b_offset = 0x174C  # Example offset
                
                self.write_value(entity_ptr + glow_r_offset, 1.0, "float")
                self.write_value(entity_ptr + glow_g_offset, 0.0, "float")
                self.write_value(entity_ptr + glow_b_offset, 0.0, "float")
        
        except Exception as e:
            self.logger.error(f"Error updating ESP: {e}")
