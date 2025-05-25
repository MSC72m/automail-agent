import platform
from pathlib import Path
from typing import Optional, List

from src.browser.interfaces import IBrowserFinder
from src.schemas.browser import BrowserConfig
from src.schemas.enums import BrowserType


class ChromeFinder(IBrowserFinder):
    def find_executable(self) -> Optional[str]:
        os_type = platform.system().lower()
        
        if os_type == "linux":
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium"
            ]
        elif os_type == "windows":
            paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            ]
        else:
            return None
        
        for path in paths:
            if Path(path).exists():
                return path
        
        return None


class EdgeFinder(IBrowserFinder):
    def find_executable(self) -> Optional[str]:
        os_type = platform.system().lower()
        
        if os_type == "linux":
            paths = [
                "/usr/bin/microsoft-edge",
                "/usr/bin/microsoft-edge-stable"
            ]
        elif os_type == "windows":
            paths = [
                "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
            ]
        else:
            return None
        
        for path in paths:
            if Path(path).exists():
                return path
        
        return None


class BraveFinder(IBrowserFinder):
    def find_executable(self) -> Optional[str]:
        os_type = platform.system().lower()
        
        if os_type == "linux":
            paths = [
                "/usr/bin/brave-browser",
                "/usr/bin/brave"
            ]
        elif os_type == "windows":
            paths = [
                "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
                "C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
            ]
        else:
            return None
        
        for path in paths:
            if Path(path).exists():
                return path
        
        return None


class FirefoxFinder(IBrowserFinder):
    def find_executable(self) -> Optional[str]:
        os_type = platform.system().lower()
        
        if os_type == "linux":
            paths = [
                "/usr/bin/firefox",
                "/usr/bin/firefox-esr"
            ]
        elif os_type == "windows":
            paths = [
                "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
            ]
        else:
            return None
        
        for path in paths:
            if Path(path).exists():
                return path
        
        return None


class AutoFinder(IBrowserFinder):
    def __init__(self):
        self.finders = [
            ChromeFinder(),
            EdgeFinder(),
            BraveFinder(),
            FirefoxFinder()
        ]
    
    def find_executable(self) -> Optional[str]:
        for finder in self.finders:
            executable = finder.find_executable()
            if executable:
                return executable
        return None
    
    def find_all_browsers(self) -> dict:
        browsers = {}
        browser_types = [
            (ChromeFinder(), BrowserType.CHROME),
            (EdgeFinder(), BrowserType.EDGE),
            (BraveFinder(), BrowserType.BRAVE),
            (FirefoxFinder(), BrowserType.FIREFOX)
        ]
        
        for finder, browser_type in browser_types:
            executable = finder.find_executable()
            if executable:
                browsers[browser_type] = executable
        
        return browsers


class BrowserFinderFactory:
    """Factory for creating browser finders based on OS type."""
    
    @classmethod
    def create_finder(cls, config: BrowserConfig) -> IBrowserFinder:
        """Create a browser finder for the given configuration."""
        if config.browser_name == BrowserType.CHROME:
            return ChromeFinder()
        elif config.browser_name == BrowserType.EDGE:
            return EdgeFinder()
        elif config.browser_name == BrowserType.BRAVE:
            return BraveFinder()
        elif config.browser_name == BrowserType.FIREFOX:
            return FirefoxFinder()
        else:
            return AutoFinder() 