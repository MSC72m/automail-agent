import os
from src.schemas.enums import OSType, BrowserType


class BrowserProfileResolver:
    """Utility class for resolving browser profile directories across different operating systems."""
    # Chromium-based browsers share similar profile directory structures
    chromium_based = {BrowserType.CHROME, BrowserType.CHROMIUM, BrowserType.EDGE, BrowserType.BRAVE}

    @classmethod
    def get_profile_dir(cls, possible_profile_dirs: list[str], browser_name: BrowserType, os_type: OSType) -> str:
        """Get the profile directory for the given browser and OS combination."""
        for dir in possible_profile_dirs:
            if os.path.exists(dir):
                return dir
        raise ValueError(f"No profile directory found for {browser_name} on {os_type}")

    @classmethod
    def get_profile_dirs(cls, browser_name: BrowserType, os_type: OSType) -> list[str]:
        """Get possible profile directories for the given browser and OS combination."""
        # Chromium-based browsers share similar profile directory structures
        
        if browser_name in cls.chromium_based:
            return cls._get_chromium_profile_dirs(browser_name, os_type)
        elif browser_name == BrowserType.FIREFOX:
            return cls._get_firefox_profile_dirs(os_type)
        elif browser_name == BrowserType.SAFARI:
            return cls._get_safari_profile_dirs(os_type)
        else:
            raise ValueError(f"Unsupported browser type: {browser_name}")
    
    @classmethod
    def get_chromium_based(cls):
        return cls.chromium_based
    
    @classmethod
    def _get_chromium_profile_dirs(cls, browser_name: BrowserType, os_type: OSType) -> list[str]:
        """Get profile directories for Chromium-based browsers (Chrome, Chromium, Edge, Brave)"""
        match os_type:
            case OSType.LINUX:
                dirs = [
                    os.path.expanduser("~/.config/google-chrome"),
                    os.path.expanduser("~/.config/google-chrome-stable"),
                    os.path.expanduser("~/.config/chromium")
                ]
                if browser_name == BrowserType.BRAVE:
                    dirs.extend([
                        os.path.expanduser("~/.config/BraveSoftware/Brave-Browser"),
                        os.path.expanduser("~/.config/brave")
                    ])
                elif browser_name == BrowserType.EDGE:
                    dirs.append(os.path.expanduser("~/.config/microsoft-edge"))
                return dirs
            case OSType.WINDOWS:
                dirs = [
                    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
                    os.path.expandvars(r"%LOCALAPPDATA%\Chromium\User Data")
                ]
                if browser_name == BrowserType.BRAVE:
                    dirs.append(os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data"))
                elif browser_name == BrowserType.EDGE:
                    dirs.append(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data"))
                return dirs
            case OSType.MACOS:
                dirs = [
                    os.path.expanduser("~/Library/Application Support/Google/Chrome"),
                    os.path.expanduser("~/Library/Application Support/Chromium")
                ]
                if browser_name == BrowserType.BRAVE:
                    dirs.append(os.path.expanduser("~/Library/Application Support/BraveSoftware/Brave-Browser"))
                elif browser_name == BrowserType.EDGE:
                    dirs.append(os.path.expanduser("~/Library/Application Support/Microsoft Edge"))
                return dirs
            case _:
                raise ValueError(f"Unsupported OS type: {os_type}")
    
    @classmethod
    def _get_firefox_profile_dirs(cls, os_type: OSType) -> list[str]:
        """Get profile directories for Firefox"""
        match os_type:
            case OSType.LINUX:
                return [
                    os.path.expanduser("~/.mozilla/firefox"),
                    os.path.expanduser("~/.firefox")
                ]
            case OSType.WINDOWS:
                return [
                    os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles"),
                    os.path.expandvars(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles")
                ]
            case OSType.MACOS:
                return [
                    os.path.expanduser("~/Library/Application Support/Firefox/Profiles")
                ]
            case _:
                raise ValueError(f"Unsupported OS type: {os_type}")
    
    @classmethod
    def _get_safari_profile_dirs(cls, os_type: OSType) -> list[str]:
        """Get profile directories for Safari (macOS only)"""
        match os_type:
            case OSType.MACOS:
                return [
                    os.path.expanduser("~/Library/Safari"),
                    os.path.expanduser("~/Library/Containers/com.apple.Safari/Data/Library/Safari")
                ]
            case _:
                raise ValueError(f"Safari is only supported on macOS, not {os_type}")
