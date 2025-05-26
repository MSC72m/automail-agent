import platform
from pathlib import Path
from typing import List, Optional

from browser.interfaces.interfaces import IBrowserProfileManager
from src.schemas.browser import BrowserConfig
from src.schemas.enums import BrowserType


class BaseBrowserProfileManager(IBrowserProfileManager):
    """Base class for browser profile managers."""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
        
        
        os_type = platform.system().lower()
        if os_type not in ["linux", "windows"]:
            raise RuntimeError(f"Unsupported operating system: {os_type}. Only Windows and Linux are supported.")
        
        
        if self.config.browser_name not in [BrowserType.CHROME, BrowserType.FIREFOX]:
            raise RuntimeError(f"Unsupported browser: {self.config.browser_name}. Only Chrome and Firefox are supported.")
    
    def get_available_profiles(self) -> List[str]:
        raise NotImplementedError
    
    def get_profile_path(self, profile_name: str) -> Optional[str]:
        raise NotImplementedError
    
    def create_profile_if_needed(self, profile_name: str) -> bool:
        profile_path = self.get_profile_path(profile_name)
        if profile_path and not Path(profile_path).exists():
            Path(profile_path).mkdir(parents=True, exist_ok=True)
            return True
        return False


class ChromeProfileManager(BaseBrowserProfileManager):
    """Profile manager for Chrome browser on Windows and Linux."""
    
    def get_available_profiles(self) -> List[str]:
        config_dir = self._get_config_directory()
        if not config_dir or not config_dir.exists():
            return ["Default"]
        
        profiles = []
        
        for item in config_dir.iterdir():
            if item.is_dir():
                if item.name == "Default" or item.name.startswith("Profile "):
                    profiles.append(item.name)
        
        return profiles if profiles else ["Default"]
    
    def get_profile_path(self, profile_name: str) -> Optional[str]:
        config_dir = self._get_config_directory()
        if not config_dir:
            return None
        
        profile_path = config_dir / profile_name
        return str(profile_path)
    
    def _get_config_directory(self) -> Optional[Path]:
        os_type = platform.system().lower()
        home = Path.home()
        
        if os_type == "linux":
            return home / ".config" / "google-chrome"
        elif os_type == "windows":
            return home / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
        
        return None


class FirefoxProfileManager(BaseBrowserProfileManager):
    """Profile manager for Firefox browser on Windows and Linux."""
    
    def get_available_profiles(self) -> List[str]:
        config_dir = self._get_config_directory()
        if not config_dir or not config_dir.exists():
            return ["default"]
        
        profiles_ini = config_dir / "profiles.ini"
        if not profiles_ini.exists():
            return ["default"]
        
        profiles = []
        try:
            with open(profiles_ini, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for line in content.split('\n'):
                if line.startswith('Name='):
                    profile_name = line.split('=', 1)[1].strip()
                    profiles.append(profile_name)
        
        except Exception:
            return ["default"]
        
        return profiles if profiles else ["default"]
    
    def get_profile_path(self, profile_name: str) -> Optional[str]:
        config_dir = self._get_config_directory()
        if not config_dir:
            return None
        
        profiles_ini = config_dir / "profiles.ini"
        if not profiles_ini.exists():
            return None
        
        try:
            with open(profiles_ini, 'r', encoding='utf-8') as f:
                content = f.read()
            
            sections = content.split('[')
            for section in sections:
                if f'Name={profile_name}' in section:
                    for line in section.split('\n'):
                        if line.startswith('Path='):
                            path = line.split('=', 1)[1].strip()
                            if line.startswith('IsRelative=1'):
                                return str(config_dir / path)
                            else:
                                return path
        
        except Exception:
            pass
        
        return None
    
    def _get_config_directory(self) -> Optional[Path]:
        os_type = platform.system().lower()
        home = Path.home()
        
        if os_type == "linux":
            return home / ".mozilla" / "firefox"
        elif os_type == "windows":
            return home / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
        
        return None


class DefaultProfileManager(BaseBrowserProfileManager):
    """Default profile manager fallback."""
    
    def get_available_profiles(self) -> List[str]:
        return ["Default"]
    
    def get_profile_path(self, profile_name: str) -> Optional[str]:
        return "Default"


class ProfileManagerFactory:
    """Factory for creating profile managers for supported browsers."""
    
    @classmethod
    def create_manager(cls, config: BrowserConfig) -> IBrowserProfileManager:
        if config.browser_name == BrowserType.CHROME:
            return ChromeProfileManager(config)
        elif config.browser_name == BrowserType.FIREFOX:
            return FirefoxProfileManager(config)
        else:
            raise ValueError(f"Unsupported browser: {config.browser_name}. Only Chrome and Firefox are supported.") 