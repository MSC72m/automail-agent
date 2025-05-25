from pydantic import BaseModel
from os import expanduser, expandvars

from src.schemas.enums import OSType, BrowserType
from src.schemas.base import BrowserProfileResolver

class BrowserConfig(BaseModel):
    browser_name: BrowserType
    headless: bool
    os_type: OSType
    browser_path: str
    
    @property
    def possible_profile_dirs(self) -> list[str]:
        """Get possible profile directories for this browser configuration."""
        return BrowserProfileResolver.get_profile_dirs(self.browser_name, self.os_type)
