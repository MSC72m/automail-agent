"""
Browser process managers for handling browser instances and debug ports.

This module implements process management strategies for different browsers,
handling debug port management, process lifecycle, and browser instance control.
"""

import os
import signal
import socket
import subprocess
import time
import psutil
from typing import Optional, List, Dict, Any
import logging

from src.browser.interfaces import IBrowserProcessManager
from src.schemas.browser import BrowserConfig
from src.schemas.enums import BrowserType, OSType

logger = logging.getLogger(__name__)


class BaseBrowserProcessManager(IBrowserProcessManager):
    """Base class for browser process managers."""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
        self._active_processes: Dict[int, psutil.Process] = {}
    
    def is_debug_port_available(self, port: int) -> bool:
        """Check if a debug port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0  
        except Exception as e:
            logger.debug(f"Error checking port {port}: {e}")
            return True  
    
    def kill_existing_instances(self, debug_port: Optional[int] = None) -> bool:
        """Kill existing browser instances."""
        killed_any = False
        
        try:
            
            process_names = self._get_browser_process_names()
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    if not proc_info['name'] or not proc_info['cmdline']:
                        continue
                    
                    
                    if any(name.lower() in proc_info['name'].lower() for name in process_names):
                        
                        if debug_port is not None:
                            cmdline = ' '.join(proc_info['cmdline'])
                            if f'--remote-debugging-port={debug_port}' not in cmdline:
                                continue
                        
                        logger.debug(f"Killing browser process {proc_info['pid']}: {proc_info['name']}")
                        proc.terminate()
                        
                        
                        try:
                            proc.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            proc.kill()  
                        
                        killed_any = True
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception as e:
                    logger.debug(f"Error killing process: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error during process cleanup: {e}")
        
        
        if killed_any:
            time.sleep(2)
        
        return killed_any
    
    def launch_with_debug_port(self, executable_path: str, profile_path: str, 
                              debug_port: int, additional_args: Optional[List[str]] = None) -> Optional[subprocess.Popen]:
        """Launch browser with debug port."""
        args = self._build_launch_args(executable_path, profile_path, debug_port, additional_args)
        
        try:
            logger.debug(f"Launching browser with args: {' '.join(args)}")
            
            
            process = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
            
            
            time.sleep(2)
            
            
            if process.poll() is not None:
                logger.error(f"Browser process exited immediately with code {process.returncode}")
                return None
            
            
            try:
                psutil_proc = psutil.Process(process.pid)
                self._active_processes[process.pid] = psutil_proc
            except psutil.NoSuchProcess:
                logger.warning(f"Could not find psutil process for PID {process.pid}")
            
            logger.info(f"Successfully launched browser with PID {process.pid} on debug port {debug_port}")
            return process
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            return None
    
    def _get_browser_process_names(self) -> List[str]:
        """Get possible process names for the browser."""
        raise NotImplementedError
    
    def _build_launch_args(self, executable_path: str, profile_path: str, 
                          debug_port: int, additional_args: Optional[List[str]] = None) -> List[str]:
        """Build command line arguments for launching the browser."""
        raise NotImplementedError


class ChromiumBasedProcessManager(BaseBrowserProcessManager):
    """Process manager for Chromium-based browsers."""
    
    
    PROCESS_NAMES = {
        BrowserType.CHROME: ["chrome", "google-chrome", "google-chrome-stable"],
        BrowserType.CHROMIUM: ["chromium", "chromium-browser"],
        BrowserType.EDGE: ["msedge", "microsoft-edge", "microsoft-edge-stable"],
        BrowserType.BRAVE: ["brave", "brave-browser"],
    }
    
    def _get_browser_process_names(self) -> List[str]:
        """Get process names for Chromium-based browsers."""
        return self.PROCESS_NAMES.get(self.config.browser_name, [self.config.browser_name.value])
    
    def _build_launch_args(self, executable_path: str, profile_path: str, 
                          debug_port: int, additional_args: Optional[List[str]] = None) -> List[str]:
        """Build launch arguments for Chromium-based browsers."""
        args = [executable_path]
        
        
        args.extend([
            f"--remote-debugging-port={debug_port}",
            f"--user-data-dir={profile_path}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
            "--disable-popup-blocking",
            "--disable-translate",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--disable-hang-monitor",
            "--disable-prompt-on-repost",
            "--disable-sync",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--disable-extensions-except",
            "--disable-component-extensions-with-background-pages",
        ])
        
        
        if self.config.headless:
            args.extend([
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ])
        
        
        if self.config.os_type == OSType.LINUX:
            args.extend([
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu-sandbox",
            ])
        
        
        if additional_args:
            args.extend(additional_args)
        
        return args


class FirefoxProcessManager(BaseBrowserProcessManager):
    """Process manager for Firefox browser."""
    
    def _get_browser_process_names(self) -> List[str]:
        """Get process names for Firefox."""
        return ["firefox", "firefox-esr"]
    
    def _build_launch_args(self, executable_path: str, profile_path: str, 
                          debug_port: int, additional_args: Optional[List[str]] = None) -> List[str]:
        """Build launch arguments for Firefox."""
        args = [executable_path]
        
        
        args.extend([
            "--remote-debugging-port", str(debug_port),
            "--profile", profile_path,
            "--no-remote",
            "--new-instance",
        ])
        
        
        if self.config.headless:
            args.append("--headless")
        
        
        if additional_args:
            args.extend(additional_args)
        
        return args


class SafariProcessManager(BaseBrowserProcessManager):
    """Process manager for Safari browser (macOS only)."""
    
    def _get_browser_process_names(self) -> List[str]:
        """Get process names for Safari."""
        return ["Safari"]
    
    def is_debug_port_available(self, port: int) -> bool:
        """Safari doesn't use debug ports in the same way."""
        return True
    
    def kill_existing_instances(self, debug_port: Optional[int] = None) -> bool:
        """Kill existing Safari instances."""
        
        try:
            subprocess.run(["osascript", "-e", 'quit app "Safari"'], 
                         capture_output=True, timeout=10)
            time.sleep(2)
            return True
        except Exception as e:
            logger.debug(f"Error quitting Safari: {e}")
            return False
    
    def launch_with_debug_port(self, executable_path: str, profile_path: str, 
                              debug_port: int, additional_args: Optional[List[str]] = None) -> Optional[subprocess.Popen]:
        """Launch Safari (limited automation support)."""
        
        
        try:
            subprocess.run([
                "defaults", "write", "com.apple.Safari", 
                "IncludeDevelopMenu", "-bool", "true"
            ], check=True)
            
            subprocess.run([
                "defaults", "write", "com.apple.Safari", 
                "WebKitDeveloperExtrasEnabledPreferenceKey", "-bool", "true"
            ], check=True)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not enable Safari developer features: {e}")
        
        
        try:
            process = subprocess.Popen([executable_path], 
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
            time.sleep(3)  
            return process
        except Exception as e:
            logger.error(f"Failed to launch Safari: {e}")
            return None
    
    def _build_launch_args(self, executable_path: str, profile_path: str, 
                          debug_port: int, additional_args: Optional[List[str]] = None) -> List[str]:
        """Build launch arguments for Safari."""
        
        return [executable_path]


class BrowserProcessManagerFactory:
    """Factory for creating browser process managers."""
    
    @classmethod
    def create_manager(cls, config: BrowserConfig) -> IBrowserProcessManager:
        """Create a process manager for the given browser configuration."""
        if config.browser_name in [BrowserType.CHROME, BrowserType.CHROMIUM, BrowserType.EDGE, BrowserType.BRAVE]:
            return ChromiumBasedProcessManager(config)
        elif config.browser_name == BrowserType.FIREFOX:
            return FirefoxProcessManager(config)
        elif config.browser_name == BrowserType.SAFARI:
            if config.os_type != OSType.MACOS:
                raise ValueError("Safari is only supported on macOS")
            return SafariProcessManager(config)
        else:
            raise ValueError(f"Unsupported browser type: {config.browser_name}") 