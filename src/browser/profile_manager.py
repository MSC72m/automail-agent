import os
import platform
from typing import List

from src.browser.interfaces.profile_manager_interfaces import IProfileManager
from src.schemas.browser import BrowserConfig
from src.schemas.enums import BrowserType
from src.utils.logger import get_logger
from src.utils.wsl_helper import is_wsl

logger = get_logger(__name__)

class ProfileManager(IProfileManager):
    """Manages browser profile operations and discovery."""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
        
    def get_original_profile_dir(self) -> str:
        """Get the original browser profile directory."""
        os_type = platform.system().lower()
        home = os.path.expanduser("~")
        
        # Check if we're in a Docker container with WSL environment
        is_wsl_env = os.environ.get('IS_WSL') == 'true' or is_wsl()
        
        if self.config.browser_name == BrowserType.CHROME:
            if os_type == "linux":
                # In Docker on WSL, check for Windows profiles first
                if is_wsl_env:
                    windows_profile_path = os.path.join(home, ".config", "google-chrome-windows")
                    if os.path.exists(windows_profile_path):
                        logger.info(f"Using Windows Chrome profile path in Docker: {windows_profile_path}")
                        return windows_profile_path
                
                # Fallback to Linux profile path
                linux_profile_path = os.path.join(home, ".config", "google-chrome")
                return linux_profile_path
            elif os_type == "windows":
                return os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data")
        elif self.config.browser_name == BrowserType.FIREFOX:
            if os_type == "linux":
                # In Docker on WSL, check for Windows profiles first
                if is_wsl_env:
                    windows_profile_path = os.path.join(home, ".mozilla", "firefox-windows")
                    if os.path.exists(windows_profile_path):
                        logger.info(f"Using Windows Firefox profile path in Docker: {windows_profile_path}")
                        return windows_profile_path
                
                # Fallback to Linux profile path
                linux_profile_path = os.path.join(home, ".mozilla", "firefox")
                return linux_profile_path
            elif os_type == "windows":
                return os.path.join(home, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles")
        
        raise ValueError(f"Unsupported browser/OS combination: {self.config.browser_name}/{os_type}")
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available profiles for the current browser."""
        if self.config.browser_name == BrowserType.CHROME:
            return self._get_chrome_profiles()
        elif self.config.browser_name == BrowserType.FIREFOX:
            return self._get_firefox_profiles()
        else:
            return ["Default"]
    
    def _get_chrome_profiles(self) -> List[str]:
        """Get list of available Chrome profiles."""
        profiles = []
        
        # Get all possible profile directories
        profile_dirs = self._get_all_chrome_profile_dirs()
        
        for original_profile_dir in profile_dirs:
            try:
                if os.path.exists(original_profile_dir):
                    logger.debug(f"Scanning Chrome profiles in: {original_profile_dir}")
                    all_items = os.listdir(original_profile_dir)
                    
                    for item in all_items:
                        profile_path = os.path.join(original_profile_dir, item)
                        if os.path.isdir(profile_path):
                            preferences_file = os.path.join(profile_path, "Preferences")
                            if os.path.exists(preferences_file):
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
                logger.warning(f"Error scanning profiles in {original_profile_dir}: {e}")
                continue
        
        # Ensure Default is always available and at the top
        if "Default" not in profiles:
            profiles.insert(0, "Default")
        elif "Default" in profiles:
            profiles.remove("Default")
            profiles.insert(0, "Default")
        
        logger.info(f"Found {len(profiles)} Chrome profiles: {profiles}")
        return profiles
    
    def _get_all_chrome_profile_dirs(self) -> List[str]:
        """Get all possible Chrome profile directories."""
        os_type = platform.system().lower()
        home = os.path.expanduser("~")
        is_wsl_env = os.environ.get('IS_WSL') == 'true' or is_wsl()
        
        profile_dirs = []
        
        if os_type == "linux":
            # Standard Linux path
            profile_dirs.append(os.path.join(home, ".config", "google-chrome"))
            
            # WSL/Docker Windows path
            if is_wsl_env:
                profile_dirs.append(os.path.join(home, ".config", "google-chrome-windows"))
        elif os_type == "windows":
            profile_dirs.append(os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data"))
        
        return profile_dirs
    
    def _get_firefox_profiles(self) -> List[str]:
        """Get list of available Firefox profiles."""
        profiles = []
        
        # Get all possible profile directories
        profile_dirs = self._get_all_firefox_profile_dirs()
        
        for original_profile_dir in profile_dirs:
            try:
                if os.path.exists(original_profile_dir):
                    logger.debug(f"Scanning Firefox profiles in: {original_profile_dir}")
                    profiles_ini = os.path.join(original_profile_dir, "profiles.ini")
                    if os.path.exists(profiles_ini):
                        with open(profiles_ini, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        for line in content.split('\n'):
                            if line.startswith('Name='):
                                profile_name = line.split('=', 1)[1].strip()
                                excluded_profiles = ["System Profile"]
                                
                                if (profile_name not in excluded_profiles and 
                                    not profile_name.startswith("chrome-automation-") and
                                    not profile_name.startswith("firefox-automation-") and
                                    profile_name not in profiles):  # Avoid duplicates
                                    profiles.append(profile_name)
                
            except Exception as e:
                logger.warning(f"Error scanning Firefox profiles in {original_profile_dir}: {e}")
                continue
        
        # Ensure default is always available and at the top
        if "default" not in [p.lower() for p in profiles]:
            profiles.insert(0, "default")
        else:
            default_profile = next((p for p in profiles if p.lower() == "default"), None)
            if default_profile:
                profiles.remove(default_profile)
                profiles.insert(0, default_profile)
        
        logger.info(f"Found {len(profiles)} Firefox profiles: {profiles}")
        return profiles
    
    def _get_all_firefox_profile_dirs(self) -> List[str]:
        """Get all possible Firefox profile directories."""
        os_type = platform.system().lower()
        home = os.path.expanduser("~")
        is_wsl_env = os.environ.get('IS_WSL') == 'true' or is_wsl()
        
        profile_dirs = []
        
        if os_type == "linux":
            # Standard Linux path
            profile_dirs.append(os.path.join(home, ".mozilla", "firefox"))
            
            # WSL/Docker Windows path
            if is_wsl_env:
                profile_dirs.append(os.path.join(home, ".mozilla", "firefox-windows"))
        elif os_type == "windows":
            profile_dirs.append(os.path.join(home, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles"))
        
        return profile_dirs