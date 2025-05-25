from enum import StrEnum, auto

class OSType(StrEnum):
    WINDOWS = auto()
    LINUX = auto()
    MAC = auto()

class BrowserType(StrEnum):
    CHROME = auto()
    CHROMIUM = auto()
    EDGE = auto()
    BRAVE = auto()
    FIREFOX = auto()
    SAFARI = auto()
