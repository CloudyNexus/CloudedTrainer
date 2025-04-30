import os
import logging
import psutil
import glob
import json
from pathlib import Path

class GameScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.steam_path = self._find_steam_path()
        self.lutris_path = self._find_lutris_path()
        self.installed_games = []
        self.running_games = []
        self.game_signatures = self._load_game_signatures()
        
        # Initial scan
        self.refresh()
    
    def refresh(self):
        """Refresh the list of installed and running games"""
        self.installed_games = self._scan_installed_games()
        self.running_games = self._scan_running_games()
    
    def get_installed_games(self):
        """Return the list of installed games"""
        return self.installed_games
    
    def get_running_games(self):
        """Return the list of running games"""
        return self.running_games
    
    def get_game_info(self, game_name):
        """Get detailed information about a specific game"""
        for game in self.installed_games:
            if game.get('name') == game_name:
                return game
        return None
    
    def is_game_running(self, game_name):
        """Check if a specific game is currently running"""
        for game in self.running_games:
            if game.get('name') == game_name:
                return True
        return False
    
    def _find_steam_path(self):
        """Find the Steam installation directory"""
        # Common Steam installation paths on Linux
        possible_paths = [
            os.path.expanduser("~/.steam"),
            os.path.expanduser("~/.local/share/Steam"),
            "/usr/share/steam"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"Found Steam installation at {path}")
                return path
        
        self.logger.warning("Steam installation not found")
        return None
    
    def _find_lutris_path(self):
        """Find the Lutris games directory"""
        lutris_path = os.path.expanduser("~/.local/share/lutris/games")
        if os.path.exists(lutris_path):
            self.logger.info(f"Found Lutris games at {lutris_path}")
            return lutris_path
        
        self.logger.warning("Lutris games directory not found")
        return None
    
    def _load_game_signatures(self):
        """Load game signatures for detection"""
        # This would ideally load from a database or file
        # For now, we'll hardcode some common game signatures
        return {
            "Counter-Strike: Global Offensive": {
                "process_names": ["csgo_linux64"],
                "steam_appid": "730",
                "executable_patterns": ["**/csgo_linux64"]
            },
            "Dota 2": {
                "process_names": ["dota2"],
                "steam_appid": "570",
                "executable_patterns": ["**/dota2"]
            },
            "Team Fortress 2": {
                "process_names": ["hl2_linux"],
                "steam_appid": "440",
                "executable_patterns": ["**/hl2_linux"]
            },
            "Minecraft": {
                "process_names": ["java", "javaw"],
                "executable_patterns": ["**/minecraft-launcher"]
            },
            "Terraria": {
                "process_names": ["Terraria.bin.x86_64", "Terraria.bin.x86"],
                "steam_appid": "105600",
                "executable_patterns": ["**/Terraria.bin.x86_64", "**/Terraria.bin.x86"]
            }
        }
    
    def _scan_installed_games(self):
        """Scan for installed games"""
        games = []
        
        # Scan Steam games if Steam is installed
        if self.steam_path:
            steam_games = self._scan_steam_games()
            games.extend(steam_games)
        
        # Scan Lutris games if Lutris is installed
        if self.lutris_path:
            lutris_games = self._scan_lutris_games()
            games.extend(lutris_games)
        
        # Scan for other known games
        other_games = self._scan_other_games()
        games.extend(other_games)
        
        self.logger.info(f"Found {len(games)} installed games")
        return games
    
    def _scan_steam_games(self):
        """Scan for installed Steam games"""
        games = []
        
        # Check if steam_path is None
        if not self.steam_path:
            self.logger.warning("Steam path is None, cannot scan Steam games")
            return games
            
        # Path to the Steam library folders configuration
        libraryfolders_path = os.path.join(self.steam_path, "steamapps", "libraryfolders.vdf")
        
        if not os.path.exists(libraryfolders_path):
            # Try another potential location
            libraryfolders_path = os.path.join(self.steam_path, "steam", "steamapps", "libraryfolders.vdf")
            if not os.path.exists(libraryfolders_path):
                self.logger.warning("Steam library folders configuration not found")
                return games
        
        # Parse the libraryfolders.vdf file (simple approach)
        library_paths = [os.path.join(self.steam_path, "steamapps")]
        try:
            with open(libraryfolders_path, 'r') as f:
                content = f.read()
                # Very basic parsing - in a real implementation, use a proper VDF parser
                for line in content.splitlines():
                    if '"path"' in line:
                        path = line.split('"path"')[1].strip().strip('"').strip()
                        if path:
                            steamapps_path = os.path.join(path, "steamapps")
                            if os.path.exists(steamapps_path):
                                library_paths.append(steamapps_path)
        except Exception as e:
            self.logger.error(f"Error parsing Steam library folders: {e}")
        
        # Scan each library path for games
        for library_path in library_paths:
            manifest_files = glob.glob(os.path.join(library_path, "appmanifest_*.acf"))
            for manifest_file in manifest_files:
                try:
                    with open(manifest_file, 'r') as f:
                        content = f.read()
                        
                        # Simple parsing for name and appid
                        name_match = None
                        appid_match = None
                        
                        for line in content.splitlines():
                            if '"name"' in line:
                                name_match = line.split('"name"')[1].strip().strip('"').strip()
                            if '"appid"' in line:
                                appid_match = line.split('"appid"')[1].strip().strip('"').strip()
                        
                        if name_match and appid_match:
                            install_dir = os.path.join(library_path, "common", name_match)
                            if not os.path.exists(install_dir):
                                # Try to find the install directory another way
                                for line in content.splitlines():
                                    if '"installdir"' in line:
                                        install_dir_name = line.split('"installdir"')[1].strip().strip('"').strip()
                                        install_dir = os.path.join(library_path, "common", install_dir_name)
                                        break
                            
                            # Check if this game has a known signature
                            process_name = None
                            for game_name, signature in self.game_signatures.items():
                                if signature.get("steam_appid") == appid_match or name_match in game_name:
                                    process_name = signature.get("process_names", [""])[0]
                                    break
                            
                            games.append({
                                "name": name_match,
                                "platform": "Steam",
                                "install_path": install_dir,
                                "appid": appid_match,
                                "process_name": process_name or name_match.lower().replace(" ", "_"),
                                "icon_path": ""  # Steam icons would need additional processing
                            })
                except Exception as e:
                    self.logger.error(f"Error parsing Steam manifest {manifest_file}: {e}")
        
        return games
    
    def _scan_lutris_games(self):
        """Scan for installed Lutris games"""
        games = []
        
        try:
            config_path = os.path.expanduser("~/.config/lutris/games")
            if os.path.exists(config_path):
                config_files = glob.glob(os.path.join(config_path, "*.yml"))
                
                for config_file in config_files:
                    try:
                        game_name = os.path.basename(config_file).split('.')[0]
                        
                        # In a real implementation, parse the YAML file properly
                        # For now, we'll just use the filename as the game name
                        
                        games.append({
                            "name": game_name,
                            "platform": "Lutris",
                            "install_path": f"{self.lutris_path}/{game_name}",
                            "process_name": game_name.lower().replace(" ", "_"),
                            "icon_path": ""  # Lutris icons would need additional processing
                        })
                    except Exception as e:
                        self.logger.error(f"Error parsing Lutris config {config_file}: {e}")
        except Exception as e:
            self.logger.error(f"Error scanning Lutris games: {e}")
        
        return games
    
    def _scan_other_games(self):
        """Scan for other known games not installed through Steam or Lutris"""
        games = []
        
        # Common locations to check for Minecraft
        minecraft_paths = [
            os.path.expanduser("~/.minecraft"),
            os.path.expanduser("~/.var/app/com.mojang.Minecraft/.minecraft")
        ]
        
        for path in minecraft_paths:
            if os.path.exists(path):
                games.append({
                    "name": "Minecraft",
                    "platform": "Other",
                    "install_path": path,
                    "process_name": "java",
                    "icon_path": ""
                })
                break
        
        return games
    
    def _scan_running_games(self):
        """Scan for currently running games"""
        running_games = []
        
        # Get all running processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                process_name = proc.info['name']
                cmdline = proc.info.get('cmdline', [])
                
                # Check against our game signatures
                for game_name, signature in self.game_signatures.items():
                    process_names = signature.get("process_names", [])
                    
                    if process_name in process_names:
                        # Found a running game
                        running_games.append({
                            "name": game_name,
                            "pid": proc.info['pid'],
                            "process_name": process_name,
                            "cmdline": cmdline
                        })
                        break
                
                # Also check our installed games list
                for game in self.installed_games:
                    if game.get("process_name") == process_name:
                        # Check if we already added this game
                        if not any(g.get("name") == game.get("name") for g in running_games):
                            running_games.append({
                                "name": game.get("name"),
                                "pid": proc.info['pid'],
                                "process_name": process_name,
                                "cmdline": cmdline
                            })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        self.logger.info(f"Found {len(running_games)} running games")
        return running_games
