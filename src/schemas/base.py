from abc import ABC
from os import expanduser, expandvars
from typing import Protocol

from src.schemas.enums import OSType, BrowserType


class BrowserProfileResolver:
    """Utility class for resolving browser profile directories across different operating systems."""
    
    @classmethod
    def get_profile_dirs(cls, browser_name: BrowserType, os_type: OSType) -> list[str]:
        """Get possible profile directories for the given browser and OS combination."""
        # Chromium-based browsers share similar profile directory structures
        chromium_based = {BrowserType.CHROME, BrowserType.CHROMIUM, BrowserType.EDGE, BrowserType.BRAVE}
        
        if browser_name in chromium_based:
            return cls._get_chromium_profile_dirs(browser_name, os_type)
        elif browser_name == BrowserType.FIREFOX:
            return cls._get_firefox_profile_dirs(os_type)
        elif browser_name == BrowserType.SAFARI:
            return cls._get_safari_profile_dirs(os_type)
        else:
            raise ValueError(f"Unsupported browser type: {browser_name}")
    
    @classmethod
    def _get_chromium_profile_dirs(cls, browser_name: BrowserType, os_type: OSType) -> list[str]:
        """Get profile directories for Chromium-based browsers (Chrome, Chromium, Edge, Brave)"""
        match os_type:
            case OSType.LINUX:
                dirs = [
                    expanduser("~/.config/google-chrome"),
                    expanduser("~/.config/google-chrome-stable"),
                    expanduser("~/.config/chromium")
                ]
                if browser_name == BrowserType.BRAVE:
                    dirs.extend([
                        expanduser("~/.config/BraveSoftware/Brave-Browser"),
                        expanduser("~/.config/brave")
                    ])
                elif browser_name == BrowserType.EDGE:
                    dirs.append(expanduser("~/.config/microsoft-edge"))
                return dirs
            case OSType.WINDOWS:
                dirs = [
                    expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
                    expandvars(r"%LOCALAPPDATA%\Chromium\User Data")
                ]
                if browser_name == BrowserType.BRAVE:
                    dirs.append(expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data"))
                elif browser_name == BrowserType.EDGE:
                    dirs.append(expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data"))
                return dirs
            case OSType.MACOS:
                dirs = [
                    expanduser("~/Library/Application Support/Google/Chrome"),
                    expanduser("~/Library/Application Support/Chromium")
                ]
                if browser_name == BrowserType.BRAVE:
                    dirs.append(expanduser("~/Library/Application Support/BraveSoftware/Brave-Browser"))
                elif browser_name == BrowserType.EDGE:
                    dirs.append(expanduser("~/Library/Application Support/Microsoft Edge"))
                return dirs
            case _:
                raise ValueError(f"Unsupported OS type: {os_type}")
    
    @classmethod
    def _get_firefox_profile_dirs(cls, os_type: OSType) -> list[str]:
        """Get profile directories for Firefox"""
        match os_type:
            case OSType.LINUX:
                return [
                    expanduser("~/.mozilla/firefox"),
                    expanduser("~/.firefox")
                ]
            case OSType.WINDOWS:
                return [
                    expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles"),
                    expandvars(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles")
                ]
            case OSType.MACOS:
                return [
                    expanduser("~/Library/Application Support/Firefox/Profiles")
                ]
            case _:
                raise ValueError(f"Unsupported OS type: {os_type}")
    
    @classmethod
    def _get_safari_profile_dirs(cls, os_type: OSType) -> list[str]:
        """Get profile directories for Safari (macOS only)"""
        match os_type:
            case OSType.MACOS:
                return [
                    expanduser("~/Library/Safari"),
                    expanduser("~/Library/Containers/com.apple.Safari/Data/Library/Safari")
                ]
            case _:
                raise ValueError(f"Safari is only supported on macOS, not {os_type}")
