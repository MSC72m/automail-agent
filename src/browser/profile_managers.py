"""
Browser profile managers for different browsers.

This module implements profile management strategies for various browsers,
handling profile creation, discovery, and path resolution.
"""

import platform
from pathlib import Path
from typing import List, Optional

from src.browser.interfaces import IBrowserProfileManager
from src.schemas.browser import BrowserConfig
from src.schemas.enums import BrowserType


class BaseBrowserProfileManager(IBrowserProfileManager):
    """Base class for browser profile managers."""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
    
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


class ChromiumBasedProfileManager(BaseBrowserProfileManager):
    """Profile manager for Chromium-based browsers (Chrome, Edge, Brave, etc.)."""
    
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
        
        if self.config.browser_name == BrowserType.CHROME:
            if os_type == "linux":
                return home / ".config" / "google-chrome"
            elif os_type == "darwin":
                return home / "Library" / "Application Support" / "Google" / "Chrome"
            elif os_type == "windows":
                return home / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
        
        elif self.config.browser_name == BrowserType.EDGE:
            if os_type == "linux":
                return home / ".config" / "microsoft-edge"
            elif os_type == "darwin":
                return home / "Library" / "Application Support" / "Microsoft Edge"
            elif os_type == "windows":
                return home / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data"
        
        elif self.config.browser_name == BrowserType.BRAVE:
            if os_type == "linux":
                return home / ".config" / "BraveSoftware" / "Brave-Browser"
            elif os_type == "darwin":
                return home / "Library" / "Application Support" / "BraveSoftware" / "Brave-Browser"
            elif os_type == "windows":
                return home / "AppData" / "Local" / "BraveSoftware" / "Brave-Browser" / "User Data"
        
        return None


class FirefoxProfileManager(BaseBrowserProfileManager):
    """Profile manager for Firefox browser."""
    
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
        elif os_type == "darwin":
            return home / "Library" / "Application Support" / "Firefox" / "Profiles"
        elif os_type == "windows":
            return home / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
        
        return None


class ChromeProfileManager(ChromiumBasedProfileManager):
    pass


class EdgeProfileManager(ChromiumBasedProfileManager):
    pass


class BraveProfileManager(ChromiumBasedProfileManager):
    pass


class DefaultProfileManager(BaseBrowserProfileManager):
    
    def get_available_profiles(self) -> List[str]:
        return ["Default"]
    
    def get_profile_path(self, profile_name: str) -> Optional[str]:
        return "Default"


class ProfileManagerFactory:
    
    @classmethod
    def create_manager(cls, config: BrowserConfig) -> IBrowserProfileManager:
        if config.browser_name == BrowserType.CHROME:
            return ChromeProfileManager(config)
        elif config.browser_name == BrowserType.EDGE:
            return EdgeProfileManager(config)
        elif config.browser_name == BrowserType.BRAVE:
            return BraveProfileManager(config)
        elif config.browser_name == BrowserType.FIREFOX:
            return FirefoxProfileManager(config)
        else:
            return DefaultProfileManager(config) 