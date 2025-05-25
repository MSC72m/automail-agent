from pydantic import BaseModel, Field
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

    @property
    def os_type(self) -> OSType:
        match platform:
            case "linux" | "linux2":
                return OSType.LINUX
            case "win32" | "cygwin" | "win64" | "win":
                return OSType.WINDOWS
            case _:
                raise ValueError(f"Unsupported OS: {platform}")
