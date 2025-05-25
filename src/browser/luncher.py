from abc import ABC, abstractmethod
import os
import sys
import glob
import subprocess
from playwright.async_api import async_playwright
from typing import Optional
import logging

from src.browser.base import BrowserInstanceFinder
from src.schemas.enums import OSType

logger = logging.getLogger(__name__)

class LinuxBrowserInstanceFinder(BrowserInstanceFinder):
    def __init__(self, os_type: OSType = OSType.WINDOWS):
        super().__init__(os_type)
        self.__browser_location = None

    @property
    def browser_location(self) -> Optional[str]:
        if self.__browser_location is None:
            self.__browser_location = self._find_browser_location()
        return self.__browser_location
    
    def _find_browser_location(self) -> Optional[str]:
        # More specific Chrome naming to avoid false positives
        if self.browser_name.lower() == "chrome":
            possible_locs = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/local/bin/google-chrome",
                "/usr/local/bin/google-chrome-stable",
                "/snap/bin/google-chrome",
            ]
            
            # Check if chrome is in PATH
            try:
                result = subprocess.run(["which", "google-chrome"], capture_output=True, text=True)
                if result.returncode == 0:
                    chrome_path = result.stdout.strip()
                    if chrome_path:
                        possible_locs.insert(0, chrome_path)
            except:
                pass
                
            # Also try "chrome" executable if google-chrome is not found
            try:
                result = subprocess.run(["which", "chrome"], capture_output=True, text=True)
                if result.returncode == 0:
                    chrome_path = result.stdout.strip()
                    if chrome_path and "gnome-shell" not in chrome_path:  # Exclude chrome-gnome-shell
                        possible_locs.append(chrome_path)
            except:
                pass
        else:
            # Standard locations for other browsers
            possible_locs = [
                f"/usr/bin/{self.browser_name}",
                f"/usr/local/bin/{self.browser_name}",
                f"/usr/bin/{self.browser_name}-stable",
                f"/snap/bin/{self.browser_name}",
            ]
        
        # Check standard locations first
        for loc in possible_locs:
            if os.path.exists(loc):
                return loc
        
        # Try pattern matching for additional possibilities
        pattern_matches = []
        for pattern in [f"/usr/bin/{self.browser_name}*", f"/usr/local/bin/{self.browser_name}*"]:
            matches = glob.glob(pattern)
            # Filter out false positives
            for match in matches:
                if os.path.basename(match) != f"{self.browser_name}-gnome-shell":
                    pattern_matches.append(match)
        
        if pattern_matches:
            return pattern_matches[0]  # Return the first match
            
        return None

    def find_instance(self) -> Optional[str]:
        print(f"Finding {self.browser_name} browser instance for Linux")
        return self.browser_location


class WindowsBrowserInstanceFinder(BrowserInstanceFinder):
    def __init__(self, browser_name: str):
        super().__init__(browser_name)
        self.__browser_location = None

    @property
    def browser_location(self) -> Optional[str]:
        if self.__browser_location is None:
            self.__browser_location = self._find_browser_location()
        return self.__browser_location
    
    def _find_browser_location(self) -> Optional[str]:
        # Chrome is typically installed in Program Files
        possible_locs = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        
        # Check standard locations first
        for loc in possible_locs:
            if os.path.exists(loc):
                return loc
        
        # Try pattern matching for additional possibilities
        pattern_matches = []
        for pattern in [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome*\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome*\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome*\Application\chrome.exe"),
        ]:
            pattern_matches.extend(glob.glob(pattern))
        
        if pattern_matches:
            return pattern_matches[0]  # Return the first match
            
        return None

    def find_instance(self) -> Optional[str]:
        print(f"Finding {self.browser_name} browser instance for Windows")
        return self.browser_location


class BrowserFinderFactory:
    @staticmethod
    def create_finder(os_type: OSType) -> BrowserInstanceFinder:
        match os_type:
            case OSType.LINUX:
                return LinuxBrowserInstanceFinder(os_type)
            case OSType.WINDOWS:
                return WindowsBrowserInstanceFinder(os_type)
            case _:
                raise ValueError(f"Unsupported OS type: {os_type}")
    



class BrowserLauncher:
    def __init__(self, os_type: OSType):
        self.finder = BrowserFinderFactory.create_finder(os_type)
        self.browser_path = self.finder.find_instance()
        
        # Use the user's existing Chrome profile directory
        if self.browser_name.lower() == "chrome":
            if sys.platform.startswith('linux'):
                # Default Chrome profile locations on Linux
                possible_profile_dirs = [
                    os.path.expanduser("~/.config/google-chrome"),
                    os.path.expanduser("~/.config/google-chrome-stable"),
                    os.path.expanduser("~/.config/chromium")
                ]
            elif sys.platform.startswith('win'):
                # Default Chrome profile locations on Windows
                possible_profile_dirs = [
                    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
                    os.path.expandvars(r"%LOCALAPPDATA%\Chromium\User Data")
                ]
            elif sys.platform.startswith('darwin'):  # macOS
                # Default Chrome profile locations on macOS
                possible_profile_dirs = [
                    os.path.expanduser("~/Library/Application Support/Google/Chrome"),
                    os.path.expanduser("~/Library/Application Support/Chromium")
                ]
            else:
                possible_profile_dirs = []
                
            # Find the first existing profile directory
            self.user_data_dir = None
            for dir_path in possible_profile_dirs:
                if os.path.exists(dir_path):
                    self.user_data_dir = dir_path
                    break
                    
            # Fallback to a custom directory if no existing profile is found
            if not self.user_data_dir:
                self.user_data_dir = os.path.expanduser(f"~/.automail-agent/browser_data/{browser_name.lower()}")
                os.makedirs(self.user_data_dir, exist_ok=True)
        else:
            # For other browsers, use a custom directory
            self.user_data_dir = os.path.expanduser(f"~/.automail-agent/browser_data/{browser_name.lower()}")
            os.makedirs(self.user_data_dir, exist_ok=True)
    
    @property
    def os_type(self):
        return sys.platform
        
    async def launch_and_navigate(self, url: str = "https://gmail.com"):

        if not self.browser_path:
            print(f"Could not find {self.browser_name} browser executable")
            return None
        
        print(f"Found browser at: {self.browser_path}")
        print(f"Using browser profile from: {self.user_data_dir}")
        print(f"Launching browser and navigating to {url}")
        
        async with async_playwright() as p:
            try:
                if self.browser_name.lower() == "chrome":
                    # Get the default profile directory (usually 'Default' or 'Profile 1')
                    default_profile = "Default"
                    profiles_dir = os.path.join(self.user_data_dir, "Default")
                    if not os.path.exists(profiles_dir):
                        # Try to find any profile directory
                        profile_dirs = [d for d in os.listdir(self.user_data_dir) 
                                       if os.path.isdir(os.path.join(self.user_data_dir, d)) 
                                       and (d.startswith("Profile") or d == "Default")]
                        if profile_dirs:
                            default_profile = profile_dirs[0]
                    
                    chrome_args = [
                        self.browser_path,
                        f"--profile-directory={default_profile}",
                        f"--user-data-dir={self.user_data_dir}",
                        url
                    ]
                    
                    print(f"Launching Chrome with args: {' '.join(chrome_args)}")
                    process = subprocess.Popen(chrome_args)
                    
                    print(f"Successfully launched Chrome with your profile")
                    print("Your browser should now be open with Gmail. Close it manually when done.")
                    print("This script will wait until you press Enter to exit...")
                    input("Press Enter to exit the script...")
                    
                    # Don't kill the process - let the user close the browser manually
                    return
                    
                # Fallback to Playwright if the direct launch fails or for other browsers
                print("Using Playwright to launch browser...")
                if self.browser_name.lower() == "chrome":
                    browser_context = await p.chromium.launch_persistent_context(
                        user_data_dir=self.user_data_dir,
                        headless=False,
                        channel="chrome",
                        args=[
                            "--no-sandbox",
                            "--disable-extensions",
                            "--disable-features=IsolateOrigins",
                            "--disable-site-isolation-trials"
                        ]
                    )
                elif self.browser_name.lower() == "firefox":
                    browser_context = await p.firefox.launch_persistent_context(
                        user_data_dir=self.user_data_dir,
                        headless=False
                    )
                else:
                    browser_context = await p.chromium.launch_persistent_context(
                        user_data_dir=self.user_data_dir,
                        headless=False,
                        executable_path=self.browser_path
                    )
                
                # Use the first page or create a new one
                if browser_context.pages:
                    page = browser_context.pages[0]
                else:
                    page = await browser_context.new_page()
                
                # Navigate to the URL
                await page.goto(url, wait_until="networkidle")
                
                print(f"Successfully navigated to {url}")
                
                await browser_context.close()
                
            except Exception as e:
                print(f"Error during browser launch: {e}")
                print("Trying simpler approach...")
                try:
                    # Simplest approach - just launch the browser directly
                    import subprocess
                    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
                        subprocess.Popen([self.browser_path, url])
                    elif sys.platform.startswith('win'):
                        subprocess.Popen([self.browser_path, url])
                        
                    print("Browser launched directly. Please close it manually when done.")
                    input("Press Enter to exit the script...")
                except Exception as e2:
                    print(f"Failed to launch browser: {e2}")
                    return None
