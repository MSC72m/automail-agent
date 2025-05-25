from enum import Enum

class StrEnum(str, Enum):
    def __str__(self):
        return self.value

class OSType(StrEnum):
    """Supported operating systems: Windows and Linux only."""
    WINDOWS = "windows"
    LINUX = "linux"

class BrowserType(StrEnum):
    """Supported browsers: Chrome and Firefox only."""
    CHROME = "chrome"
    FIREFOX = "firefox"
