import logging
import importlib
import inspect
import os
import psutil
from trainers.base_trainer import BaseTrainer
from memory_manager import MemoryManager

class TrainerManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.trainers = {}
        self.active_trainers = {}
        self.memory_manager = MemoryManager()
        
        # Load all available trainers
        self._load_trainers()
    
    def _load_trainers(self):
        """Load all trainer classes from the trainers package"""
        try:
            # Import all trainer modules
            from trainers import csgo_trainer, dota2_trainer, minecraft_trainer, tf2_trainer, terraria_trainer
            
            # List of all trainer modules
            trainer_modules = [
                csgo_trainer,
                dota2_trainer,
                minecraft_trainer,
                tf2_trainer,
                terraria_trainer
            ]
            
            # Find all trainer classes in the modules
            for module in trainer_modules:
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, BaseTrainer) and obj != BaseTrainer:
                        # Instantiate the trainer
                        trainer_instance = obj(self.memory_manager)
                        self.trainers[trainer_instance.game_name] = trainer_instance
                        self.logger.info(f"Loaded trainer: {trainer_instance.name} for {trainer_instance.game_name}")
            
            self.logger.info(f"Loaded {len(self.trainers)} trainers")
        except Exception as e:
            self.logger.error(f"Error loading trainers: {e}")
    
    def get_available_trainers(self):
        """Get a list of all available trainers"""
        return list(self.trainers.values())
    
    def get_trainer(self, game_name):
        """Get a specific trainer by game name"""
        return self.trainers.get(game_name)
    
    def get_available_cheats(self, game_name):
        """Get available cheats for a specific game"""
        trainer = self.trainers.get(game_name)
        if not trainer:
            return []
        
        return trainer.get_available_cheats()
    
    def toggle_cheat(self, game_name, cheat_id, enable=True):
        """Toggle a specific cheat for a game"""
        trainer = self.trainers.get(game_name)
        if not trainer:
            self.logger.error(f"No trainer available for {game_name}")
            return False
        
        # Find the running process
        process_name = trainer.process_name
        target_pid = None
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == process_name:
                    target_pid = proc.info['pid']
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if not target_pid:
            self.logger.error(f"Game process {process_name} not found running")
            return False
        
        # Check if we're already attached to this game
        if game_name not in self.active_trainers:
            # Attach to the game process
            success = self.memory_manager.attach(target_pid)
            if not success:
                self.logger.error(f"Failed to attach to process {target_pid}")
                return False
            
            # Initialize the trainer
            success = trainer.initialize()
            if not success:
                self.logger.error(f"Failed to initialize trainer for {game_name}")
                self.memory_manager.detach()
                return False
            
            self.active_trainers[game_name] = {
                "pid": target_pid,
                "trainer": trainer,
                "active_cheats": set()
            }
        
        # Toggle the cheat
        if enable:
            success = trainer.enable_cheat(cheat_id)
            if success:
                self.active_trainers[game_name]["active_cheats"].add(cheat_id)
        else:
            success = trainer.disable_cheat(cheat_id)
            if success and cheat_id in self.active_trainers[game_name]["active_cheats"]:
                self.active_trainers[game_name]["active_cheats"].remove(cheat_id)
        
        # If no cheats are active, detach from the process
        if not self.active_trainers[game_name]["active_cheats"]:
            self.memory_manager.detach()
            del self.active_trainers[game_name]
        
        return success
    
    def update_all_active_trainers(self):
        """Update all active trainers (called periodically)"""
        # Make a copy to avoid modification during iteration
        active_trainers_copy = dict(self.active_trainers)
        
        for game_name, trainer_info in active_trainers_copy.items():
            pid = trainer_info["pid"]
            trainer = trainer_info["trainer"]
            
            # Check if the process is still running
            if not psutil.pid_exists(pid):
                self.logger.info(f"Game {game_name} with PID {pid} is no longer running")
                # Game process has ended, clean up
                if game_name in self.active_trainers:
                    del self.active_trainers[game_name]
                continue
            
            # Update the trainer
            try:
                trainer.update()
            except Exception as e:
                self.logger.error(f"Error updating trainer for {game_name}: {e}")
    
    def cleanup(self):
        """Cleanup and detach from all processes"""
        for game_name in list(self.active_trainers.keys()):
            self.memory_manager.detach()
            del self.active_trainers[game_name]
