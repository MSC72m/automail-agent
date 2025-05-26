from typing import Optional, List
import subprocess
import os

from src.browser.interfaces.finders_interfaces import IBrowserFinder
from src.schemas.browser import BrowserConfig
from src.schemas.enums import BrowserType, OSType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseBrowserFinder(IBrowserFinder):
    """Base class for browser finders."""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
    
    def find_browser_executable(self) -> Optional[str]:
        """Find the browser executable path."""
        for path in self.get_possible_paths():
            if os.path.exists(path):
                return path
        return None
    
    def get_possible_paths(self) -> List[str]:
        """Get possible paths for the browser executable."""
        raise NotImplementedError("Subclasses must implement get_possible_paths")


class ChromeFinder(BaseBrowserFinder):
    """Chrome browser finder."""
    
    def get_possible_paths(self) -> List[str]:
        """Get possible Chrome executable paths."""
        if self.config.os_type == OSType.LINUX:
            possible_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/local/bin/google-chrome",
                "/snap/bin/google-chrome",
            ]
            
            try:
                # Check if google-chrome is installed in the system
                result = subprocess.run(["which", "google-chrome"], capture_output=True, text=True)
                if result.returncode == 0:
                    chrome_path = result.stdout.strip()
                    if chrome_path and chrome_path not in possible_paths:
                        possible_paths.insert(0, chrome_path)
            except subprocess.CalledProcessError:
                logger.warning("Warning: Could not find Chrome executable path")
            
            return possible_paths
            
        elif self.config.os_type == OSType.WINDOWS:
            return [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            ]
        else:
            return []


class FirefoxFinder(BaseBrowserFinder):
    """Firefox browser finder."""
    
    def get_possible_paths(self) -> List[str]:
        """Get possible Firefox executable paths."""
        if self.config.os_type == OSType.LINUX:
            return [
                "/usr/bin/firefox",
                "/usr/bin/firefox-esr",
                "/usr/local/bin/firefox",
                "/snap/bin/firefox",
            ]
        elif self.config.os_type == OSType.WINDOWS:
            return [
                os.path.expandvars(r"%ProgramFiles%\Mozilla Firefox\firefox.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"),
            ]
        else:
            return []


class BrowserFinder:
    """Main browser finder that delegates to specific browser finders."""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
        self._finder = self._get_finder()
    
    def _get_finder(self) -> BaseBrowserFinder:
        """Get the appropriate finder for the browser type."""
        if self.config.browser_name == BrowserType.CHROME:
            return ChromeFinder(self.config)
        elif self.config.browser_name == BrowserType.FIREFOX:
            return FirefoxFinder(self.config)
        else:
            raise ValueError(f"Unsupported browser: {self.config.browser_name}")
    
    def find_browser_executable(self) -> Optional[str]:
        """Find the browser executable path."""
        return self._finder.find_browser_executable()