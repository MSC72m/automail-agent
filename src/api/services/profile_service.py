import logging
from typing import List, Optional

from src.api.services.interfaces.profile_interface import ProfileServiceInterface
from src.schemas.profile import BrowserProfile, ProfileListResponse
from src.schemas.enums import BrowserType
from src.schemas.browser import BrowserConfig
from src.browser.launchers import BrowserLauncher
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ProfileService(ProfileServiceInterface):
    """Profile service implementation for browser profile management"""
    
    def __init__(self):
        self._cached_profiles = {}
    
    async def get_available_profiles(self, browser_type: Optional[BrowserType] = None) -> ProfileListResponse:
        """Get list of available browser profiles"""
        try:
            profiles = []
            
            if browser_type:
                browser_types = [browser_type]
            else:
                browser_types = list(BrowserType)
            
            for bt in browser_types:
                try:
                    browser_config = BrowserConfig(browser_name=bt, headless=False)
                    launcher = BrowserLauncher(browser_config)
                    available_profiles = launcher.get_available_profiles()
                    
                    for profile_name in available_profiles:
                        profile = BrowserProfile(
                            name=profile_name,
                            browser_type=bt,
                            path=profile_name,  
                            is_default=(profile_name.lower() in ["default", "default profile"]),
                            description=f"{bt.value.title()} profile: {profile_name}"
                        )
                        profiles.append(profile)
                            
                except Exception as e:
                    logger.warning(f"Error getting profiles for {bt}: {e}")
                    continue
            
            if not profiles:
                for bt in browser_types:
                    default_profile = BrowserProfile(
                        name="Default",
                        browser_type=bt,
                        path="default",
                        is_default=True,
                        description=f"Default {bt.value.title()} profile"
                    )
                    profiles.append(default_profile)
            
            return ProfileListResponse(
                profiles=profiles,
                total_count=len(profiles)
            )
            
        except Exception as e:
            logger.error(f"Error getting available profiles: {e}")
            return ProfileListResponse(profiles=[], total_count=0)
    
    async def get_profile_by_name(self, profile_name: str, browser_type: BrowserType) -> Optional[BrowserProfile]:
        """Get a specific profile by name and browser type"""
        try:
            profiles_response = await self.get_available_profiles(browser_type)
            
            for profile in profiles_response.profiles:
                if profile.name == profile_name and profile.browser_type == browser_type:
                    return profile
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting profile by name: {e}")
            return None
    
    async def get_default_profile(self, browser_type: BrowserType) -> Optional[BrowserProfile]:
        """Get the default profile for a browser type"""
        try:
            profiles_response = await self.get_available_profiles(browser_type)
            
            for profile in profiles_response.profiles:
                if profile.browser_type == browser_type and profile.is_default:
                    return profile
            
            for profile in profiles_response.profiles:
                if profile.browser_type == browser_type:
                    return profile
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting default profile: {e}")
            return None
    
    async def validate_profile_exists(self, profile_name: str, browser_type: BrowserType) -> bool:
        """Validate if a profile exists"""
        try:
            profile = await self.get_profile_by_name(profile_name, browser_type)
            return profile is not None
        except Exception as e:
            logger.error(f"Error validating profile exists: {e}")
            return False 