import os
import platform
from typing import List

from src.browser.interfaces.profile_manager_interfaces import IProfileManager
from src.schemas.browser import BrowserConfig
from src.core.enums import BrowserType, OSType
from src.core.logger import get_logger
from src.core.wsl_helper import is_wsl

logger = get_logger(__name__)

class BaseProfileManager:
    def __init__(self, config: BrowserConfig):
        self.config = config
        self._home = self.config.home
        self._os_type = self.config.os_type
    
    def _get_chrome_profile_dir(self) -> str: ...

    def _get_firefox_profile_dir(self) -> str: ...

    def get_original_profile_dir(self) -> str:
        match self.config.browser_name:
            case BrowserType.CHROME:
                return self._get_chrome_profile_dir()
            case BrowserType.FIREFOX:
                return self._get_firefox_profile_dir()
            case _:
                raise ValueError(f"Unsupported browser: {self.config.browser_name}")


class LinuxProfileManager(BaseProfileManager):
    def __init__(self, config: BrowserConfig):
        self.config = config
        self._is_wsl = self.config.is_wsl
        self._home = self.config.home
    
    def _get_chrome_profile_dir(self) -> str:
        # In Docker on WSL, check for Windows profiles first
        if self._is_wsl:
            windows_profile_path = os.path.join(self._home, ".config", "google-chrome-windows")
            if os.path.exists(windows_profile_path):
                logger.info(f"Using Windows Chrome profile path in Docker: {windows_profile_path}")
                return windows_profile_path
        
        # Fallback to Linux profile path
        linux_profile_path = os.path.join(self._home, ".config", "google-chrome")
        return linux_profile_path
    
    def _get_firefox_profile_dir(self) -> str:
        # In Docker on WSL, check for Windows profiles first
        if self._is_wsl:
            windows_profile_path = os.path.join(self._home, ".mozilla", "firefox-windows")
            if os.path.exists(windows_profile_path):
                logger.info(f"Using Windows Firefox profile path in Docker: {windows_profile_path}")
                return windows_profile_path
        
        # Fallback to Linux profile path
        linux_profile_path = os.path.join(self._home, ".mozilla", "firefox")
        return linux_profile_path

class WindowsProfileManager(BaseProfileManager):
    def __init__(self, config: BrowserConfig):
        self.config = config
        self._home = self.config.home
    
    def _get_chrome_profile_dir(self) -> str:
        return os.path.join(self._home, "AppData", "Local", "Google", "Chrome", "User Data")
    
    def _get_firefox_profile_dir(self) -> str:
        return os.path.join(self._home, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles")

class ProfileManagerFactory:
    def __init__(self, config: BrowserConfig):
        self.config = config

    def get_profile_manager(self) -> BaseProfileManager:
        match self.config.os_type:
            case OSType.LINUX:
                return LinuxProfileManager(self.config)
            case OSType.WINDOWS:
                return WindowsProfileManager(self.config)
            case _:
                raise ValueError(f"Unsupported OS: {self.config.os_type}")

class ProfileManager(IProfileManager):
    """Manages browser profile operations and discovery."""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
        self._profile_manager = ProfileManagerFactory(self.config).get_profile_manager()
    
    @property
    def original_profile_dir(self) -> str:
        """Get the original browser profile directory."""
        return self._profile_manager.get_original_profile_dir()
    
    def _is_valid_chrome_profile(self, profile_path: str) -> bool:
        """Check if a directory is a valid Chrome profile."""
        preferences_file = os.path.join(profile_path, "Preferences")
        return os.path.exists(preferences_file)
    
    def _is_valid_firefox_profile(self, profile_path: str) -> bool:
        """Check if a directory is a valid Firefox profile."""
        # Firefox profiles contain prefs.js or user.js files
        prefs_file = os.path.join(profile_path, "prefs.js")
        user_file = os.path.join(profile_path, "user.js")
        return os.path.exists(prefs_file) or os.path.exists(user_file)
    
    def _is_valid_profile(self, profile_path: str) -> bool:
        """Check if a directory is a valid browser profile based on browser type."""
        match self.config.browser_name:
            case BrowserType.CHROME:
                return self._is_valid_chrome_profile(profile_path)
            case BrowserType.FIREFOX:
                return self._is_valid_firefox_profile(profile_path)
            case _:
                return False
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available browser profiles for the configured browser."""
        profiles = []
        
        try:
            if os.path.exists(self.original_profile_dir):
                logger.debug(f"Scanning profiles in: {self.original_profile_dir}")
                all_items = os.listdir(self.original_profile_dir)
                
                for item in all_items:
                    profile_path = os.path.join(self.original_profile_dir, item)
                    if os.path.isdir(profile_path):
                        if self._is_valid_profile(profile_path):
                            excluded_profiles = [
                                "System Profile", "Guest Profile", "BrowserMetrics-spare.pma", "Automation Profile",
                                "AutomationProfile"
                            ]
                            
                            if (item not in excluded_profiles and 
                                not item.startswith("chrome-automation-") and
                                not item.startswith("firefox-automation-") and
                                item not in profiles):  # Avoid duplicates
                                profiles.append(item)
                                logger.debug(f"Added profile: {item}")
            
        except Exception as e:
            logger.warning(f"Error scanning profiles in {self.original_profile_dir}: {e}")
        
        # Ensure Default is always available and at the top
        if "Default" not in profiles:
            profiles.insert(0, "Default")
        elif "Default" in profiles:
            profiles.remove("Default")
            profiles.insert(0, "Default")
        
        logger.info(f"Found {len(profiles)} profiles: {profiles}")
        return profiles
    