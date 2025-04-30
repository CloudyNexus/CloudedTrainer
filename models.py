"""
Models for the CloudedTrainer application.

These are dictionary-style classes that mimic SQLAlchemy models
but are designed to work with the StorageManager for local storage instead.
"""
from datetime import datetime
import json

class Game:
    """Game model for storing game information."""
    
    def __init__(self, id=None, name="", process_name="", install_path="", 
                 icon_path="", platform="", created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.process_name = process_name
        self.install_path = install_path
        self.icon_path = icon_path
        self.platform = platform
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
    
    def to_dict(self):
        """Convert Game object to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "process_name": self.process_name,
            "install_path": self.install_path,
            "icon_path": self.icon_path,
            "platform": self.platform,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Game object from dictionary."""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            process_name=data.get("process_name", ""),
            install_path=data.get("install_path", ""),
            icon_path=data.get("icon_path", ""),
            platform=data.get("platform", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def __repr__(self):
        return f'<Game {self.name}>'

class Trainer:
    """Trainer model for storing trainer information."""
    
    def __init__(self, id=None, name="", game_name="", description="", 
                 process_name="", version="1.0.0", created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.game_name = game_name
        self.description = description
        self.process_name = process_name
        self.version = version
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
    
    def to_dict(self):
        """Convert Trainer object to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "game_name": self.game_name,
            "description": self.description,
            "process_name": self.process_name,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Trainer object from dictionary."""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            game_name=data.get("game_name", ""),
            description=data.get("description", ""),
            process_name=data.get("process_name", ""),
            version=data.get("version", "1.0.0"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def __repr__(self):
        return f'<Trainer {self.name} for {self.game_name}>'

class GameSession:
    """GameSession model for storing game session information."""
    
    def __init__(self, id=None, game_id=None, game_name="", start_time=None, 
                 end_time=None, active_cheats=None):
        self.id = id
        self.game_id = game_id
        self.game_name = game_name
        self.start_time = start_time or datetime.utcnow().isoformat()
        self.end_time = end_time
        self.active_cheats = active_cheats or []
    
    def to_dict(self):
        """Convert GameSession object to dictionary."""
        return {
            "id": self.id,
            "game_id": self.game_id,
            "game_name": self.game_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "active_cheats": self.active_cheats
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create GameSession object from dictionary."""
        return cls(
            id=data.get("id"),
            game_id=data.get("game_id"),
            game_name=data.get("game_name", ""),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            active_cheats=data.get("active_cheats", [])
        )
    
    def add_active_cheat(self, cheat_id):
        """Add a cheat to the active cheats list."""
        if cheat_id not in self.active_cheats:
            self.active_cheats.append(cheat_id)
    
    def remove_active_cheat(self, cheat_id):
        """Remove a cheat from the active cheats list."""
        if cheat_id in self.active_cheats:
            self.active_cheats.remove(cheat_id)
    
    def __repr__(self):
        return f'<GameSession {self.id} for Game {self.game_name}>'
