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

class LogLevel(str, Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Environment(str, Enum):
    """Environment enumeration."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"
