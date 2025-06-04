import os
import platform
import subprocess
from typing import Optional, List

from src.core.logger import get_logger
from src.core.wsl_helper import is_wsl
from src.schemas.browser import BrowserConfig
from core.enums import BrowserType, OSType

logger = get_logger(__name__)


class BaseBrowserFinder(IBrowserFinder):
    """Base class for browser finders."""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
    
    def find_browser_executable(self) -> Optional[str]:
        """Find the browser executable path."""
        for path in self.get_possible_paths():
            if os.path.exists(path):
                logger.info(f"Found browser executable: {path}")
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
            possible_paths = []
            
            # First, try to get Playwright's Chromium path
            try:
                from playwright.sync_api import sync_playwright
                p = sync_playwright().start()
                playwright_chromium = p.chromium.executable_path
                p.stop()
                if os.path.exists(playwright_chromium):
                    possible_paths.append(playwright_chromium)
                    logger.debug(f"Found Playwright Chromium: {playwright_chromium}")
            except Exception as e:
                logger.debug(f"Could not get Playwright Chromium path: {e}")
            
            # Standard Linux Chrome paths
            linux_chrome_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/local/bin/google-chrome",
                "/snap/bin/google-chrome",
            ]
            possible_paths.extend(linux_chrome_paths)
            
            # Check if we're in a WSL/Docker environment and add Windows browser paths
            # Note: These are only useful if we can actually execute them (e.g., with Wine)
            if os.environ.get('IS_WSL') == 'true' or is_wsl():
                windows_chrome_paths = [
                    "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
                    "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
                ]
                # Only add Windows paths if they exist and we can execute them
                # For now, we'll skip Windows executables in Linux containers
                # possible_paths.extend(windows_chrome_paths)
            
            try:
                # Check if google-chrome is installed in the system
                result = subprocess.run(["which", "google-chrome"], capture_output=True, text=True)
                if result.returncode == 0:
                    chrome_path = result.stdout.strip()
                    if chrome_path and chrome_path not in possible_paths:
                        possible_paths.insert(-1, chrome_path)  # Insert before Playwright as fallback
            except subprocess.CalledProcessError:
                logger.debug("Could not find Chrome executable via 'which' command")
            
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
            possible_paths = [
                "/usr/bin/firefox",
                "/usr/bin/firefox-esr",
                "/usr/local/bin/firefox",
                "/snap/bin/firefox",
            ]
            
            # Check if we're in a WSL/Docker environment and add Windows browser paths
            is_wsl_env = os.environ.get('IS_WSL') == 'true' or is_wsl()
            if is_wsl_env:
                # Add Windows Firefox paths that might be mounted in Docker
                windows_firefox_paths = [
                    "/usr/bin/firefox.exe",  # Mounted Windows Firefox
                    "/mnt/c/Program Files/Mozilla Firefox/firefox.exe",
                    "/mnt/c/Program Files (x86)/Mozilla Firefox/firefox.exe",
                ]
                # Add Windows paths at the beginning for priority
                possible_paths = windows_firefox_paths + possible_paths
            
            return possible_paths
            
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