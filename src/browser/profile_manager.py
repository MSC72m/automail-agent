import os
import platform
from typing import List

from src.browser.interfaces.profile_manager_interfaces import IProfileManager
from src.schemas.browser import BrowserConfig
from src.schemas.enums import BrowserType
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ProfileManager(IProfileManager):
    """Manages browser profile operations and discovery."""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
        
    def get_original_profile_dir(self) -> str:
        """Get the original browser profile directory."""
        os_type = platform.system().lower()
        home = os.path.expanduser("~")
        
        if self.config.browser_name == BrowserType.CHROME:
            if os_type == "linux":
                return os.path.join(home, ".config", "google-chrome")
            elif os_type == "windows":
                return os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data")
        elif self.config.browser_name == BrowserType.FIREFOX:
            if os_type == "linux":
                return os.path.join(home, ".mozilla", "firefox")
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
        original_profile_dir = self.get_original_profile_dir()
        
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
                                "System Profile", "Guest Profile", "BrowserMetrics-spare.pma"
                            ]
                            
                            if (item not in excluded_profiles and 
                                not item.startswith("chrome-automation-") and
                                not item.startswith("firefox-automation-")):
                                profiles.append(item)
                                logger.debug(f"Added profile: {item}")
            
            # Ensure Default is always available and at the top
            if "Default" not in profiles:
                profiles.insert(0, "Default")
            elif "Default" in profiles:
                profiles.remove("Default")
                profiles.insert(0, "Default")
            
            logger.info(f"Found {len(profiles)} Chrome profiles: {profiles}")
                
        except Exception as e:
            logger.warning(f"Error getting profiles: {e}")
            profiles = ["Default"]
        
        return profiles
    
    def _get_firefox_profiles(self) -> List[str]:
        """Get list of available Firefox profiles."""
        profiles = []
        original_profile_dir = self.get_original_profile_dir()
        
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
                                not profile_name.startswith("firefox-automation-")):
                                profiles.append(profile_name)
            
            # Ensure default is always available and at the top
            if "default" not in [p.lower() for p in profiles]:
                profiles.insert(0, "default")
            else:
                default_profile = next((p for p in profiles if p.lower() == "default"), None)
                if default_profile:
                    profiles.remove(default_profile)
                    profiles.insert(0, default_profile)
            
            logger.info(f"Found {len(profiles)} Firefox profiles: {profiles}")
                
        except Exception as e:
            logger.warning(f"Error getting Firefox profiles: {e}")
            profiles = ["default"]
        
        return profiles