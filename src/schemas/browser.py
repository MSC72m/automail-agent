from pydantic import BaseModel, Field, validator
from typing import Optional
import os
import platform

from src.core.wsl_helper import is_wsl
from core.enums import BrowserType, OSType

class BrowserConfig(BaseModel):
    """Configuration for browser automation."""
    
    browser_name: BrowserType = Field(
        default=BrowserType.CHROME,
        description="The name of the browser to use. Available options: chrome, firefox",
    )
    headless: bool = Field(
        default=False,
        description="Whether to run the browser in headless mode"
    )
    profile_name: str = Field(
        default="Default",
        description="The name of the browser profile to use"
    )

    @property
    def os_type(self) -> OSType:
        match platform:
            case "linux" | "linux2":
                return OSType.LINUX
            case "win32" | "cygwin" | "win64" | "win":
                return OSType.WINDOWS
            case _:
                raise ValueError(f"Unsupported OS: {platform}")
    
    @property
    def home(self) -> str:
        return os.path.expanduser("~")

    @property
    def is_wsl(self) -> bool:
        return is_wsl()

