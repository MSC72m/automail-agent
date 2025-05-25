from enum import Enum

class StrEnum(str, Enum):
    def __str__(self):
        return self.value

class OSType(StrEnum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"

class BrowserType(StrEnum):
    CHROME = "chrome"
    CHROMIUM = "chromium"
    EDGE = "edge"
    BRAVE = "brave"
    FIREFOX = "firefox"
    SAFARI = "safari"
