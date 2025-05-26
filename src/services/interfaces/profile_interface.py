from abc import ABC, abstractmethod
from typing import List, Optional
from src.schemas.profile import BrowserProfile, ProfileListResponse
from src.schemas.enums import BrowserType

class ProfileServiceInterface(ABC):
    """Abstract interface for profile services"""
    
    @abstractmethod
    async def get_available_profiles(self, browser_type: Optional[BrowserType] = None) -> ProfileListResponse:
        """Get list of available browser profiles"""
        pass
    
    @abstractmethod
    async def get_profile_by_name(self, profile_name: str, browser_type: BrowserType) -> Optional[BrowserProfile]:
        """Get a specific profile by name and browser type"""
        pass
    
    @abstractmethod
    async def get_default_profile(self, browser_type: BrowserType) -> Optional[BrowserProfile]:
        """Get the default profile for a browser type"""
        pass
    
    @abstractmethod
    async def validate_profile_exists(self, profile_name: str, browser_type: BrowserType) -> bool:
        """Validate if a profile exists"""
        pass 