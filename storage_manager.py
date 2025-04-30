import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class StorageManager:
    """
    Manages local storage for the application using JSON files instead of a database.
    This allows the application to work offline while maintaining data persistence.
    """
    
    def __init__(self, data_dir="data"):
        """Initialize the storage manager with a data directory."""
        self.data_dir = data_dir
        self._ensure_data_directory()
        self.trainers = self._load_trainers()
        self.sessions = self._load_sessions()
        self.settings = self._load_settings()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory: {self.data_dir}")
    
    def _load_trainers(self):
        """Load trainers from JSON file."""
        trainers_path = os.path.join(self.data_dir, "trainers.json")
        if os.path.exists(trainers_path):
            try:
                with open(trainers_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading trainers: {e}")
                return []
        return []
    
    def _save_trainers(self):
        """Save trainers to JSON file."""
        trainers_path = os.path.join(self.data_dir, "trainers.json")
        try:
            with open(trainers_path, 'w') as f:
                json.dump(self.trainers, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving trainers: {e}")
    
    def _load_sessions(self):
        """Load game sessions from JSON file."""
        sessions_path = os.path.join(self.data_dir, "sessions.json")
        if os.path.exists(sessions_path):
            try:
                with open(sessions_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading sessions: {e}")
                return []
        return []
    
    def _save_sessions(self):
        """Save game sessions to JSON file."""
        sessions_path = os.path.join(self.data_dir, "sessions.json")
        try:
            with open(sessions_path, 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving sessions: {e}")
    
    def _load_settings(self):
        """Load application settings from JSON file."""
        settings_path = os.path.join(self.data_dir, "settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading settings: {e}")
                return self._get_default_settings()
        return self._get_default_settings()
    
    def _save_settings(self):
        """Save application settings to JSON file."""
        settings_path = os.path.join(self.data_dir, "settings.json")
        try:
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving settings: {e}")
    
    def _get_default_settings(self):
        """Return default application settings."""
        return {
            "auto_refresh": True,
            "start_with_system": False,
            "check_updates": True,
            "scan_frequency": 30,
            "theme": "dark",
            "memory_scan_method": "ptrace",
            "log_level": "info",
            "log_path": "~/.cloudedtrainer/logs/",
            "game_paths": [
                {"name": "Steam", "path": "~/.steam/steam/steamapps"},
                {"name": "Lutris", "path": "~/.local/share/lutris/games"},
                {"name": "Custom", "path": "~/Games"}
            ]
        }
    
    def get_trainers(self):
        """Get all trainers."""
        return self.trainers
    
    def get_trainer_by_game(self, game_name):
        """Get a trainer by game name."""
        for trainer in self.trainers:
            if trainer.get("game_name") == game_name:
                return trainer
        return None
    
    def add_trainer(self, trainer):
        """Add a new trainer."""
        self.trainers.append(trainer)
        self._save_trainers()
    
    def update_trainer(self, game_name, updates):
        """Update a trainer by game name."""
        for trainer in self.trainers:
            if trainer.get("game_name") == game_name:
                trainer.update(updates)
                self._save_trainers()
                return True
        return False
    
    def delete_trainer(self, game_name):
        """Delete a trainer by game name."""
        self.trainers = [t for t in self.trainers if t.get("game_name") != game_name]
        self._save_trainers()
    
    def start_game_session(self, game_id, game_name):
        """Start a new game session."""
        session = {
            "id": len(self.sessions) + 1,
            "game_id": game_id,
            "game_name": game_name,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "active_cheats": []
        }
        self.sessions.append(session)
        self._save_sessions()
        return session
    
    def end_game_session(self, session_id):
        """End a game session by ID."""
        for session in self.sessions:
            if session.get("id") == session_id and not session.get("end_time"):
                session["end_time"] = datetime.now().isoformat()
                self._save_sessions()
                return True
        return False
    
    def add_cheat_to_session(self, session_id, cheat_id):
        """Add an active cheat to a game session."""
        for session in self.sessions:
            if session.get("id") == session_id and not session.get("end_time"):
                active_cheats = session.get("active_cheats", [])
                if cheat_id not in active_cheats:
                    active_cheats.append(cheat_id)
                    session["active_cheats"] = active_cheats
                    self._save_sessions()
                return True
        return False
    
    def remove_cheat_from_session(self, session_id, cheat_id):
        """Remove an active cheat from a game session."""
        for session in self.sessions:
            if session.get("id") == session_id and not session.get("end_time"):
                active_cheats = session.get("active_cheats", [])
                if cheat_id in active_cheats:
                    active_cheats.remove(cheat_id)
                    session["active_cheats"] = active_cheats
                    self._save_sessions()
                return True
        return False
    
    def get_active_session_for_game(self, game_name):
        """Get the active session for a game by name."""
        for session in self.sessions:
            if session.get("game_name") == game_name and not session.get("end_time"):
                return session
        return None
    
    def get_game_sessions(self, game_name):
        """Get all sessions for a game by name."""
        return [s for s in self.sessions if s.get("game_name") == game_name]
    
    def get_setting(self, key):
        """Get a setting by key."""
        return self.settings.get(key)
    
    def update_setting(self, key, value):
        """Update a setting by key."""
        self.settings[key] = value
        self._save_settings()
    
    def update_settings(self, settings_dict):
        """Update multiple settings at once."""
        self.settings.update(settings_dict)
        self._save_settings()

    def initialize_default_trainers(self, trainer_list):
        """Initialize default trainers if none exist."""
        if not self.trainers:
            for trainer_info in trainer_list:
                trainer = {
                    "id": len(self.trainers) + 1,
                    "name": trainer_info.get("name"),
                    "game_name": trainer_info.get("game_name"),
                    "description": trainer_info.get("description"),
                    "process_name": trainer_info.get("process_name"),
                    "version": "1.0.0",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                self.trainers.append(trainer)
            self._save_trainers()
            logger.info(f"Initialized {len(self.trainers)} default trainers")