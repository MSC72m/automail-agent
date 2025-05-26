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

from src.browser.interfaces.lunchers_interfaces import IBrowserLauncher
from src.browser.finders import BrowserFinder
from src.browser.profile_manager import ProfileManager
from src.schemas.browser import BrowserConfig
from src.schemas.enums import BrowserType
from src.utils.logger import get_logger

logger = get_logger(__name__)

class BrowserSetup:
    """Handles browser profile setup and configuration."""
    def __init__(self, config: BrowserConfig, profile_manager: ProfileManager):
        self.config = config
        self.profile_manager = profile_manager
        self.temp_profile_dir = None
        
    def setup_automation_profile(self, profile_name: str = "Default") -> str:
        """Set up automation profile using temporary directory."""
        try:
            logger.info("Setting up automation profile...")
            
            # Create temporary directory for automation profile
            self.temp_profile_dir = tempfile.mkdtemp(prefix=f"{self.config.browser_name.value.lower()}-automation-")
            logger.debug(f"Created temporary profile directory: {self.temp_profile_dir}")
            
            if self.config.browser_name == BrowserType.CHROME:
                self._setup_chrome_profile(profile_name)
            elif self.config.browser_name == BrowserType.FIREFOX:
                self._setup_firefox_profile()
            
            logger.info("✅ Automation profile setup complete")
            return self.temp_profile_dir
            
        except Exception as e:
            logger.warning(f"Warning: Could not set up automation profile: {e}")
            logger.info("Continuing with empty profile...")
            if not self.temp_profile_dir:
                self.temp_profile_dir = tempfile.mkdtemp(prefix=f"{self.config.browser_name.value.lower()}-automation-")
            return self.temp_profile_dir
    
    def _setup_chrome_profile(self, profile_name: str):
        """Set up Chrome automation profile."""
        original_profile_dir = self.profile_manager.get_original_profile_dir()
        available_profiles = self.profile_manager.get_available_profiles()
        
        # Determine source profile
        if profile_name and profile_name != "Default" and profile_name in available_profiles:
            source_profile = profile_name
            logger.info(f"Using user-selected profile: {source_profile}")
        else:
            source_profile = "Profile 2" if "Profile 2" in available_profiles else "Default"
        
        source_profile_path = os.path.join(original_profile_dir, source_profile)
        dest_profile_path = os.path.join(self.temp_profile_dir, "Default")
        
        logger.info(f"Setting up Chrome automation profile by copying from '{source_profile}'...")
        
        # Create destination directory
        os.makedirs(dest_profile_path, exist_ok=True)
        
        if os.path.exists(source_profile_path):
            # Copy essential files
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
            
            # Copy Local State
            local_state_source = os.path.join(original_profile_dir, "Local State")
            local_state_dest = os.path.join(self.temp_profile_dir, "Local State")
            if os.path.exists(local_state_source):
                try:
                    shutil.copy2(local_state_source, local_state_dest)
                    logger.debug("Copied Local State")
                except Exception as e:
                    logger.warning(f"Warning: Could not copy Local State: {e}")
        else:
            logger.warning(f"⚠️  Source profile not found: {source_profile_path}")
    
    def _setup_firefox_profile(self):
        """Set up Firefox automation profile."""
        dest_profile_path = os.path.join(self.temp_profile_dir, "automation-profile")
        os.makedirs(dest_profile_path, exist_ok=True)
        
        logger.info("Setting up Firefox automation profile...")
        
        # Create Firefox preferences
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
    
    def cleanup(self):
        """Clean up temporary profile directory."""
        if self.temp_profile_dir and os.path.exists(self.temp_profile_dir):
            try:
                shutil.rmtree(self.temp_profile_dir)
                logger.debug(f"Cleaned up temporary profile: {self.temp_profile_dir}")
            except Exception as e:
                logger.warning(f"Warning: Could not clean up temporary profile: {e}")
            finally:
                self.temp_profile_dir = None


class ProcessManager:
    """Manages browser process operations."""
    
    def __init__(self, config: BrowserConfig, debug_port: int):
        self.config = config
        self.debug_port = debug_port
    
    def kill_existing_instances(self):
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
    
    def is_debug_port_available(self) -> bool:
        """Check if the debug port is available."""
        try:
            response = requests.get(f"http://localhost:{self.debug_port}/json/version", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def launch_browser_process(self, browser_path: str, automation_profile_dir: str) -> subprocess.Popen:
        """Launch browser process with debug port."""
        if self.config.browser_name == BrowserType.CHROME:
            args = self._build_chrome_args(browser_path, automation_profile_dir)
        elif self.config.browser_name == BrowserType.FIREFOX:
            args = self._build_firefox_args(browser_path, automation_profile_dir)
        else:
            raise ValueError(f"Unsupported browser: {self.config.browser_name}")
        
        logger.info(f"Launching {self.config.browser_name} with automation profile on debug port {self.debug_port}")
        logger.debug(f"Command: {' '.join(args)}")
        
        # Launch process
        os_type = platform.system().lower()
        if os_type == "windows":
            return subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            return subprocess.Popen(args, preexec_fn=os.setsid if hasattr(os, 'setsid') else None)
    
    def _build_chrome_args(self, browser_path: str, automation_profile_dir: str) -> List[str]:
        """Build Chrome command line arguments."""
        args = [
            browser_path,
            f"--remote-debugging-port={self.debug_port}",
            f"--user-data-dir={automation_profile_dir}",
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
    
    def _build_firefox_args(self, browser_path: str, automation_profile_dir: str) -> List[str]:
        """Build Firefox command line arguments."""
        profile_path = os.path.join(automation_profile_dir, "automation-profile")
        
        args = [
            browser_path,
            "--remote-debugging-port", str(self.debug_port),
            "--profile", profile_path,
            "--no-remote",
            "--new-instance",
        ]
        
        if self.config.headless:
            args.append("--headless")
        
        return args


class BrowserLauncher(IBrowserLauncher):
    """Simplified browser launcher with separated concerns."""
    
    def __init__(self, config: BrowserConfig):
        """Initialize the browser launcher with configuration."""
        self.config = config
        self.debug_port = 9222
        self.browser_finder = BrowserFinder(config)
        self.profile_manager = ProfileManager(config)
        self.browser_setup = None
        self.process_manager = None
        
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._playwright = None
        self._browser_process = None
    
    async def launch(self, profile_name: str = "Default", debug_port: Optional[int] = None, 
                    additional_args: Optional[List[str]] = None) -> bool:
        """Launch the browser with the specified configuration."""
        try:
            if debug_port:
                self.debug_port = debug_port
            
            if profile_name and profile_name != "Default":
                self.config.profile_name = profile_name
                logger.info(f"Using profile: {profile_name}")
            
            logger.info(f"Launching {self.config.browser_name} browser")
            
            browser_path = self.browser_finder.find_browser_executable()
            if not browser_path:
                raise RuntimeError(f"Could not find {self.config.browser_name} browser executable")
            
            self.process_manager = ProcessManager(self.config, self.debug_port)
            self.browser_setup = BrowserSetup(self.config, self.profile_manager)
            
            self.process_manager.kill_existing_instances()
            time.sleep(1)
            
            automation_profile_dir = self.browser_setup.setup_automation_profile(profile_name)
            
            # Launch browser process
            self._browser_process = self.process_manager.launch_browser_process(browser_path, automation_profile_dir)
            logger.info(f"Browser process started with PID: {self._browser_process.pid}")
            
            max_retries = 20
            logger.info(f"Waiting for browser debug port to be ready...")
            
            for i in range(max_retries):
                if self.process_manager.is_debug_port_available():
                    logger.info(f"✅ Browser debug port {self.debug_port} is ready!")
                    break
                
                if i % 4 == 0 and i > 0:
                    logger.debug(f"Still waiting... ({i//2}s elapsed)")
                
                time.sleep(0.5)
            else:
                raise RuntimeError(f"Browser debug port {self.debug_port} did not become available after {max_retries/2} seconds")
            
            # Connect via Playwright
            if not self._playwright:
                self._playwright = await async_playwright().start()
            
            logger.info(f"Connecting to browser via CDP on port {self.debug_port}")
            if self.config.browser_name == BrowserType.CHROME:
                self._browser = await self._playwright.chromium.connect_over_cdp(f"http://localhost:{self.debug_port}")
            elif self.config.browser_name == BrowserType.FIREFOX:
                self._browser = await self._playwright.firefox.connect_over_cdp(f"http://localhost:{self.debug_port}")
            else:
                raise ValueError(f"Unsupported browser: {self.config.browser_name}")
            
            # Get or create context
            contexts = self._browser.contexts
            if contexts:
                self._context = contexts[0]
            else:
                self._context = await self._browser.new_context()
            
            logger.info(f"✅ Successfully launched {self.config.browser_name} browser")
            return True
            
        except Exception as e:
            logger.error(f"Error during browser launch: {e}")
            self.terminate()
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
    
    async def terminate(self):
        """Terminate the browser completely."""
        # Stop playwright first
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
        
        if self.process_manager:
            self.process_manager.kill_existing_instances()
        
        if self.browser_setup:
            self.browser_setup.cleanup()
        
        logger.info("✅ Browser terminated") 