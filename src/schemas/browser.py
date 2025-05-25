from pydantic import BaseModel, Field
from sys import platform

from src.schemas.enums import OSType, BrowserType
from src.schemas.base import BrowserProfileResolver

class BrowserConfig(BaseModel):
    browser_name: BrowserType = Field(
        ...,
        description="The name of the browser to use. Available options: chrome, firefox, edge, safari, opera, brave",
    )
    headless: bool = Field(
        default=True,
        description="Whether to run the browser in headless mode.",
    )

    @property
    def os_type(self) -> OSType:
        match platform:
            case "linux" | "linux2":
                return OSType.LINUX
            case "win32" | "cygwin" | "win64" | "win":
                return OSType.WINDOWS
            case "darwin":
                return OSType.MACOS
            case _:
                raise ValueError(f"Unsupported OS: {platform}")

    @property
    def chromium_base(self) -> str:
        return BrowserProfileResolver.get_chromium_based()

    @property
    def possible_profile_dirs(self) -> list[str]:
        """Get possible profile directories for this browser configuration."""
        return BrowserProfileResolver.get_profile_dirs(self.browser_name, self.os_type)
    
    @property
    def profile_dir(self) -> str:
        """Get the profile directory for this browser configuration."""
        return BrowserProfileResolver.get_profile_dir(self.possible_profile_dirs, self.browser_name, self.os_type)
