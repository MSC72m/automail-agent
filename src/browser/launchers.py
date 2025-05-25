import os
import shutil
import subprocess
import time
import platform
import psutil
import requests
import tempfile
from typing import Optional, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from src.schemas.browser import BrowserConfig
from src.schemas.enums import BrowserType, OSType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BrowserLauncher:
    """
    Simplified browser launcher that works like the original luncher.py.
    
    Supports only Chrome and Firefox with proper profile copying and automation setup
    on Windows and Linux only.
    """
    
    def __init__(self, config: BrowserConfig):
        """Initialize the browser launcher with configuration."""
        self.config = config
        self.debug_port = 9222
        
        
        if self.config.os_type not in {OSType.LINUX, OSType.WINDOWS}:
            raise RuntimeError(f"Unsupported operating system: {self.config.os_type}. Only Windows and Linux are supported.")
        
        
        if self.config.browser_name not in [BrowserType.CHROME, BrowserType.FIREFOX]:
            raise RuntimeError(f"Unsupported browser: {self.config.browser_name}. Only Chrome and Firefox are supported.")
        
        
        self.browser_path = self._find_browser_executable()
        if not self.browser_path:
            raise RuntimeError(f"Could not find {self.config.browser_name} executable")
        
        
        self.original_profile_dir = self._get_original_profile_dir()
        self.automation_profile_dir = self._get_automation_profile_dir()
        
        
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._playwright = None
        self._browser_process = None
    
    def _find_browser_executable(self) -> Optional[str]:
        """Find the browser executable path."""
        os_type = platform.system().lower()
        
        if self.config.browser_name == BrowserType.CHROME:
            if os_type == "linux":
                possible_paths = [
                    "/usr/bin/google-chrome",
                    "/usr/bin/google-chrome-stable",
                    "/usr/local/bin/google-chrome",
                    "/snap/bin/google-chrome",
                ]
                
                try:
                    result = subprocess.run(["which", "google-chrome"], capture_output=True, text=True)
                    if result.returncode == 0:
                        chrome_path = result.stdout.strip()
                        if chrome_path:
                            possible_paths.insert(0, chrome_path)
                except:
                    pass
            elif os_type == "windows":
                possible_paths = [
                    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                    os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                    os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
                ]
            else:
                return None
                
        elif self.config.browser_name == BrowserType.FIREFOX:
            if os_type == "linux":
                possible_paths = [
                    "/usr/bin/firefox",
                    "/usr/bin/firefox-esr",
                    "/usr/local/bin/firefox",
                    "/snap/bin/firefox",
                ]
            elif os_type == "windows":
                possible_paths = [
                    os.path.expandvars(r"%ProgramFiles%\Mozilla Firefox\firefox.exe"),
                    os.path.expandvars(r"%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"),
                ]
            else:
                return None
        else:
            raise ValueError(f"Unsupported browser: {self.config.browser_name}")
        
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _get_original_profile_dir(self) -> str:
        """Get the original browser profile directory."""
        os_type = platform.system().lower()
        home = os.path.expanduser("~")
        
        if self.config.browser_name == BrowserType.CHROME:
            if os_type == "linux":
                return os.path.join(home, ".config", "google-chrome")
            elif os_type == "windows":
                return os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data")
        elif self.config.browser_name == BrowserType.FIREFOX:
            if os_type == "linux":
                return os.path.join(home, ".mozilla", "firefox")
            elif os_type == "windows":
                return os.path.join(home, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles")
        
        raise ValueError(f"Unsupported browser/OS combination: {self.config.browser_name}/{os_type}")
    
    def _get_automation_profile_dir(self) -> str:
        """Get the automation profile directory in temp."""
        
        if self.config.browser_name == BrowserType.CHROME:
            return tempfile.mkdtemp(prefix="chrome-automation-")
        elif self.config.browser_name == BrowserType.FIREFOX:
            return tempfile.mkdtemp(prefix="firefox-automation-")
        else:
            return tempfile.mkdtemp(prefix=f"{self.config.browser_name.value}-automation-")
    
    def _setup_automation_profile(self):
        """Set up the automation profile by copying from the original profile."""
        try:
            logger.info("Setting up automation profile...")
            
            
            
            
            if self.config.browser_name == BrowserType.CHROME:
                self._setup_chrome_automation_profile()
            elif self.config.browser_name == BrowserType.FIREFOX:
                self._setup_firefox_automation_profile()
            
            logger.info("✅ Automation profile setup complete")
            
        except Exception as e:
            logger.warning(f"Warning: Could not set up automation profile: {e}")
            logger.info("Continuing with empty profile...")
    
    def _setup_chrome_automation_profile(self):
        """Set up Chrome automation profile."""
        
        original_profiles = self._get_chrome_profiles_from_original()
        
        
        if hasattr(self.config, 'profile_name') and self.config.profile_name != "Default":
            
            if self.config.profile_name in original_profiles:
                source_profile = self.config.profile_name
                logger.info(f"Using user-selected profile: {source_profile}")
            else:
                logger.warning(f"Requested profile '{self.config.profile_name}' not found, falling back to Default")
                source_profile = "Default"
        else:
            
            source_profile = "Profile 2" if "Profile 2" in original_profiles else "Default"
        
        source_profile_path = os.path.join(self.original_profile_dir, source_profile)
        dest_profile_path = os.path.join(self.automation_profile_dir, "Default")
        
        logger.info(f"Setting up Chrome automation profile by copying from '{source_profile}'...")
        logger.debug(f"Source: {source_profile_path}")
        logger.debug(f"Destination: {dest_profile_path}")
        
        
        os.makedirs(dest_profile_path, exist_ok=True)
        
        if os.path.exists(source_profile_path):
            
            essential_files = [
                "Cookies", "Login Data", "Web Data", "Preferences", 
                "Local State", "Secure Preferences", "Network Action Predictor",
                "History", "Top Sites", "Favicons"
            ]
            
            for file_name in essential_files:
                source_file = os.path.join(source_profile_path, file_name)
                dest_file = os.path.join(dest_profile_path, file_name)
                
                if os.path.exists(source_file):
                    try:
                        shutil.copy2(source_file, dest_file)
                        logger.debug(f"Copied {file_name}")
                    except Exception as e:
                        logger.warning(f"Warning: Could not copy {file_name}: {e}")
            
            
            local_state_source = os.path.join(self.original_profile_dir, "Local State")
            local_state_dest = os.path.join(self.automation_profile_dir, "Local State")
            if os.path.exists(local_state_source):
                try:
                    shutil.copy2(local_state_source, local_state_dest)
                    logger.debug("Copied Local State")
                except Exception as e:
                    logger.warning(f"Warning: Could not copy Local State: {e}")
        else:
            logger.warning(f"⚠️  Source profile not found: {source_profile_path}")
            logger.info("Creating empty automation profile...")
    
    def _setup_firefox_automation_profile(self):
        """Set up Firefox automation profile."""
        
        
        dest_profile_path = os.path.join(self.automation_profile_dir, "automation-profile")
        
        logger.info("Setting up Firefox automation profile...")
        logger.debug(f"Destination: {dest_profile_path}")
        
        
        os.makedirs(dest_profile_path, exist_ok=True)
        
        
        prefs_content = '''
user_pref("browser.startup.homepage", "about:blank");
user_pref("browser.startup.page", 0);
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.rights.3.shown", true);
user_pref("browser.sessionstore.resume_from_crash", false);
user_pref("datareporting.healthreport.uploadEnabled", false);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("toolkit.telemetry.enabled", false);
user_pref("toolkit.telemetry.unified", false);
'''
        
        prefs_file = os.path.join(dest_profile_path, "prefs.js")
        with open(prefs_file, 'w') as f:
            f.write(prefs_content)
        
        logger.debug("Created Firefox automation profile")
    
    def _get_chrome_profiles_from_original(self) -> List[str]:
        """Get list of available Chrome profiles from the original Chrome directory."""
        profiles = []
        try:
            if os.path.exists(self.original_profile_dir):
                for item in os.listdir(self.original_profile_dir):
                    profile_path = os.path.join(self.original_profile_dir, item)
                    if os.path.isdir(profile_path):
                        
                        preferences_file = os.path.join(profile_path, "Preferences")
                        if os.path.exists(preferences_file):
                            
                            if item not in ["System Profile", "Guest Profile"] and "automation" not in item.lower():
                                profiles.append(item)
            
            
            if "Default" not in profiles:
                profiles.insert(0, "Default")
                
        except Exception as e:
            logger.warning(f"Error getting profiles: {e}")
            profiles = ["Default"]
        
        return profiles
    
    def _kill_existing_browser_instances(self):
        """Kill any existing browser instances that might be using the debug port."""
        try:
            process_names = []
            if self.config.browser_name == BrowserType.CHROME:
                process_names = ["chrome", "google-chrome", "google-chrome-stable"]
            elif self.config.browser_name == BrowserType.FIREFOX:
                process_names = ["firefox", "firefox-esr"]
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and any(name in proc.info['name'].lower() for name in process_names):
                        cmdline = proc.info['cmdline']
                        if cmdline and any(f'--remote-debugging-port={self.debug_port}' in arg for arg in cmdline):
                            logger.info(f"Killing existing browser process with PID {proc.info['pid']}")
                            proc.kill()
                            proc.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            logger.warning(f"Error while killing existing browser instances: {e}")
    
    def _is_debug_port_available(self) -> bool:
        """Check if the debug port is available by trying to connect to it."""
        try:
            response = requests.get(f"http://localhost:{self.debug_port}/json/version", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def _launch_browser_with_debug_port(self):
        """Launch browser with debug port."""
        if not self.browser_path:
            raise RuntimeError(f"Could not find {self.config.browser_name} browser executable")
        
        
        self._kill_existing_browser_instances()
        time.sleep(1)
        
        
        self._setup_automation_profile()
        
        
        if self.config.browser_name == BrowserType.CHROME:
            args = self._build_chrome_args()
        elif self.config.browser_name == BrowserType.FIREFOX:
            args = self._build_firefox_args()
        else:
            raise ValueError(f"Unsupported browser: {self.config.browser_name}")
        
        logger.info(f"Launching {self.config.browser_name} with automation profile on debug port {self.debug_port}")
        logger.debug(f"Browser executable: {self.browser_path}")
        logger.debug(f"Command: {' '.join(args)}")
        
        try:
            
            os_type = platform.system().lower()
            if os_type == "windows":
                self._browser_process = subprocess.Popen(
                    args,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                self._browser_process = subprocess.Popen(
                    args,
                    preexec_fn=os.setsid if hasattr(os, 'setsid') else None
                )
            
            logger.info(f"Browser process started with PID: {self._browser_process.pid}")
            
            
            max_retries = 20
            logger.info(f"Waiting for browser debug port to be ready...")
            
            for i in range(max_retries):
                if self._is_debug_port_available():
                    logger.info(f"✅ Browser debug port {self.debug_port} is ready!")
                    return True
                
                if i % 4 == 0 and i > 0:  
                    logger.debug(f"Still waiting... ({i//2}s elapsed)")
                
                time.sleep(0.5)
            
            raise RuntimeError(f"Browser debug port {self.debug_port} did not become available after {max_retries/2} seconds")
            
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
            if self._browser_process and self._browser_process.poll() is None:
                self._browser_process.terminate()
                self._browser_process = None
            raise
    
    def _build_chrome_args(self) -> List[str]:
        """Build Chrome command line arguments."""
        args = [
            self.browser_path,
            f"--remote-debugging-port={self.debug_port}",
            f"--user-data-dir={self.automation_profile_dir}",
            "--profile-directory=Default",
            "--no-first-run",
            "--disable-default-apps",
            "--disable-features=VizDisplayCompositor",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding"
        ]
        
        if self.config.headless:
            args.append("--headless=new")
        
        return args
    
    def _build_firefox_args(self) -> List[str]:
        """Build Firefox command line arguments."""
        profile_path = os.path.join(self.automation_profile_dir, "automation-profile")
        
        args = [
            self.browser_path,
            "--remote-debugging-port", str(self.debug_port),
            "--profile", profile_path,
            "--no-remote",
            "--new-instance",
        ]
        
        if self.config.headless:
            args.append("--headless")
        
        return args
    
    async def launch(self, profile_name: str = "Default", debug_port: Optional[int] = None, 
                    additional_args: Optional[List[str]] = None) -> bool:
        """
        Launch the browser with the specified configuration.
        
        Args:
            profile_name: Name of the browser profile to use
            debug_port: Debug port to use (optional, defaults to 9222)
            additional_args: Additional command line arguments (optional)
            
        Returns:
            True if launch was successful, False otherwise
        """
        try:
            if debug_port:
                self.debug_port = debug_port
            
            
            if profile_name and profile_name != "Default":
                self.config.profile_name = profile_name
                logger.info(f"Using profile: {profile_name}")
            
            logger.info(f"Launching {self.config.browser_name} browser")
            
            
            self._launch_browser_with_debug_port()
            
            
            if not self._playwright:
                self._playwright = await async_playwright().start()
            
            
            logger.info(f"Connecting to browser via CDP on port {self.debug_port}")
            if self.config.browser_name == BrowserType.CHROME:
                self._browser = await self._playwright.chromium.connect_over_cdp(f"http://localhost:{self.debug_port}")
            elif self.config.browser_name == BrowserType.FIREFOX:
                self._browser = await self._playwright.firefox.connect_over_cdp(f"http://localhost:{self.debug_port}")
            else:
                raise ValueError(f"Unsupported browser: {self.config.browser_name}")
            
            
            contexts = self._browser.contexts
            if contexts:
                self._context = contexts[0]
            else:
                self._context = await self._browser.new_context()
            
            logger.info(f"✅ Successfully launched {self.config.browser_name} browser")
            return True
            
        except Exception as e:
            logger.error(f"Error during browser launch: {e}")
            await self.close()
            return False
    
    async def get_page(self) -> Optional[Page]:
        """Get the current page or create a new one."""
        if not self._browser or not self._context:
            logger.error("Browser not launched")
            return None
        
        if not self._page:
            
            pages = self._context.pages
            if pages:
                self._page = pages[0]
            else:
                self._page = await self._context.new_page()
        
        return self._page
    
    async def new_page(self) -> Optional[Page]:
        """Create a new page."""
        if not self._browser or not self._context:
            logger.error("Browser not launched")
            return None
        
        try:
            page = await self._context.new_page()
            return page
        except Exception as e:
            logger.error(f"Error creating new page: {e}")
            return None
    
    def get_browser(self) -> Optional[Browser]:
        """Get the browser instance."""
        return self._browser
    
    def get_context(self) -> Optional[BrowserContext]:
        """Get the browser context."""
        return self._context
    
    def is_running(self) -> bool:
        """Check if the browser is running."""
        return self._browser is not None and self._browser.is_connected()
    
    async def close(self):
        """Close the browser connection (but keep browser running)."""
        try:
            if self._context:
                logger.debug("Closing browser context...")
                
                self._context = None
            
            if self._browser:
                logger.debug("Disconnecting from browser...")
                
                self._browser = None
            
            if self._playwright:
                logger.debug("Stopping playwright...")
                await self._playwright.stop()
                self._playwright = None
                
            logger.info("✅ Disconnected from browser CDP session (browser will remain open)")
        except Exception as e:
            logger.warning(f"Warning during cleanup: {e}")
            
            self._context = None
            self._browser = None
            self._playwright = None
    
    async def terminate(self):
        """Terminate the browser completely."""
        
        if self._playwright:
            try:
                await self._playwright.stop()
            except:
                pass
            finally:
                self._playwright = None
        
        self._browser = None
        self._context = None
        
        if self._browser_process:
            logger.info("Terminating browser completely")
            try:
                self._browser_process.terminate()
                self._browser_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._browser_process.kill()
                self._browser_process.wait()
            except:
                pass
            finally:
                self._browser_process = None
        
        
        self._kill_existing_browser_instances()
        logger.info("✅ Browser terminated")
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available profiles for the current browser."""
        if self.config.browser_name == BrowserType.CHROME:
            return self._get_chrome_profiles_from_original()
        elif self.config.browser_name == BrowserType.FIREFOX:
            return self._get_firefox_profiles_from_original()
        else:
            return ["Default"]
    
    def _get_firefox_profiles_from_original(self) -> List[str]:
        """Get list of available Firefox profiles from the original Firefox directory."""
        profiles = []
        try:
            if os.path.exists(self.original_profile_dir):
                profiles_ini = os.path.join(self.original_profile_dir, "profiles.ini")
                if os.path.exists(profiles_ini):
                    with open(profiles_ini, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for line in content.split('\n'):
                        if line.startswith('Name='):
                            profile_name = line.split('=', 1)[1].strip()
                            
                            if profile_name not in ["System Profile", "default-release"] and "automation" not in profile_name.lower():
                                profiles.append(profile_name)
            
            
            if "default" not in [p.lower() for p in profiles]:
                profiles.insert(0, "default")
                
        except Exception as e:
            logger.warning(f"Error getting Firefox profiles: {e}")
            profiles = ["default"]
        
        return profiles 