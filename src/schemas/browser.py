from pydantic import BaseModel, Field
from typing import Optional
from sys import platform

from src.schemas.enums import OSType, BrowserType

class BrowserConfig(BaseModel):
    browser_name: BrowserType = Field(
        ...,
        description="The name of the browser to use. Available options: chrome, firefox, edge, safari, opera, brave",
    )
    headless: bool = Field(
        default=True,
        description="Whether to run the browser in headless mode.",
    )
    profile_name: Optional[str] = Field(
        default=None,
        description="The name of the browser profile to use.",
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
