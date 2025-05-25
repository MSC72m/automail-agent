"""
Main browser launcher that orchestrates all browser components.

This module provides the main BrowserLauncher class that coordinates
browser finding, profile management, process management, and Playwright integration.
"""

import asyncio
import time
from typing import Optional, List, Dict, Any
import logging

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from src.browser.interfaces import IBrowserFinder, IBrowserProfileManager, IBrowserProcessManager, IBrowserLauncher
from src.browser.finders import BrowserFinderFactory
from src.browser.profile_managers import ProfileManagerFactory
from src.browser.process_managers import BrowserProcessManagerFactory
from src.schemas.browser import BrowserConfig
from src.schemas.enums import BrowserType

logger = logging.getLogger(__name__)


class BrowserLauncher(IBrowserLauncher):
    """
    Main browser launcher that orchestrates all browser components.
    
    This class uses the Strategy pattern to coordinate different browser
    implementations and provides a unified interface for browser automation.
    """
    
    def __init__(self, config: BrowserConfig):
        """Initialize the browser launcher with configuration."""
        self.config = config
        
        
        self.finder: IBrowserFinder = BrowserFinderFactory.create_finder(config)
        self.profile_manager: IBrowserProfileManager = ProfileManagerFactory.create_manager(config)
        self.process_manager: IBrowserProcessManager = BrowserProcessManagerFactory.create_manager(config)
        
        
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._playwright = None
        self._browser_process = None
        self._debug_port: Optional[int] = None
        
        
        self._debug_port_range = range(9222, 9322)
    
    async def launch(self, profile_name: str = "Default", debug_port: Optional[int] = None, 
                    additional_args: Optional[List[str]] = None) -> bool:
        """
        Launch the browser with the specified configuration.
        
        Args:
            profile_name: Name of the browser profile to use
            debug_port: Debug port to use (auto-selected if None)
            additional_args: Additional command line arguments
            
        Returns:
            True if launch was successful, False otherwise
        """
        try:
            logger.info(f"Launching {self.config.browser_name} browser with profile '{profile_name}'")
            
            
            executable_path = self.finder.find_executable()
            if not executable_path:
                logger.error(f"Could not find {self.config.browser_name} executable")
                return False
            
            logger.debug(f"Found browser executable: {executable_path}")
            
            
            # Get the actual profile path (don't create new, use existing)
            profile_path = self.profile_manager.get_profile_path(profile_name)
            if not profile_path:
                logger.error(f"Could not find profile '{profile_name}' for {self.config.browser_name}")
                return False
            
            logger.debug(f"Using existing profile path: {profile_path}")
            
            
            if debug_port is None:
                debug_port = self._find_available_debug_port()
                if debug_port is None:
                    logger.error("Could not find available debug port")
                    return False
            
            self._debug_port = debug_port
            logger.debug(f"Using debug port: {debug_port}")
            
            
            if not self.process_manager.is_debug_port_available(debug_port):
                logger.info("Killing existing browser instances on debug port")
                self.process_manager.kill_existing_instances(debug_port)
                
                
                time.sleep(2)
                if not self.process_manager.is_debug_port_available(debug_port):
                    logger.error(f"Debug port {debug_port} is still not available")
                    return False
            
            
            self._browser_process = self.process_manager.launch_with_debug_port(
                executable_path, profile_path, debug_port, additional_args
            )
            
            if not self._browser_process:
                logger.error("Failed to launch browser process")
                return False
            
            
            await self._wait_for_browser_ready(debug_port)
            
            
            success = await self._connect_playwright(debug_port)
            if not success:
                logger.error("Failed to connect with Playwright")
                await self.close()
                return False
            
            logger.info(f"Successfully launched {self.config.browser_name} browser")
            return True
            
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
            await self.close()
            return False
    
    async def connect_to_existing(self, debug_port: int) -> bool:
        """
        Connect to an existing browser instance.
        
        Args:
            debug_port: Debug port of the existing browser instance
            
        Returns:
            True if connection was successful, False otherwise
        """
        try:
            logger.info(f"Connecting to existing {self.config.browser_name} instance on port {debug_port}")
            
            
            if self.process_manager.is_debug_port_available(debug_port):
                logger.error(f"No browser instance found on debug port {debug_port}")
                return False
            
            self._debug_port = debug_port
            
            
            success = await self._connect_playwright(debug_port)
            if not success:
                logger.error("Failed to connect with Playwright")
                return False
            
            logger.info(f"Successfully connected to existing {self.config.browser_name} instance")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to existing browser: {e}")
            return False
    
    async def close(self) -> None:
        """Close the browser and clean up resources."""
        try:
            logger.info("Closing browser")
            
            
            if self._page:
                await self._page.close()
                self._page = None
            
            if self._context:
                await self._context.close()
                self._context = None
            
            if self._browser:
                await self._browser.close()
                self._browser = None
            
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            
            
            if self._browser_process:
                try:
                    self._browser_process.terminate()
                    self._browser_process.wait(timeout=5)
                except Exception as e:
                    logger.debug(f"Error terminating browser process: {e}")
                    try:
                        self._browser_process.kill()
                    except Exception:
                        pass
                finally:
                    self._browser_process = None
            
            self._debug_port = None
            logger.info("Browser closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    async def terminate(self) -> None:
        """Forcefully terminate the browser and all related processes."""
        try:
            logger.info("Terminating browser")
            
            
            await self.close()
            
            
            if self._debug_port:
                self.process_manager.kill_existing_instances(self._debug_port)
            else:
                self.process_manager.kill_existing_instances()
            
            logger.info("Browser terminated successfully")
            
        except Exception as e:
            logger.error(f"Error terminating browser: {e}")
    
    async def get_page(self) -> Optional[Page]:
        """Get the current page or create a new one."""
        if not self._browser or not self._context:
            logger.error("Browser not launched or connected")
            return None
        
        if not self._page:
            try:
                self._page = await self._context.new_page()
                logger.debug("Created new page")
            except Exception as e:
                logger.error(f"Error creating new page: {e}")
                return None
        
        return self._page
    
    async def new_page(self) -> Optional[Page]:
        """Create a new page."""
        if not self._browser or not self._context:
            logger.error("Browser not launched or connected")
            return None
        
        try:
            page = await self._context.new_page()
            logger.debug("Created new page")
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
    
    def _find_available_debug_port(self) -> Optional[int]:
        """Find an available debug port."""
        for port in self._debug_port_range:
            if self.process_manager.is_debug_port_available(port):
                return port
        return None
    
    async def _wait_for_browser_ready(self, debug_port: int, timeout: int = 30) -> bool:
        """Wait for the browser to be ready for connections."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.process_manager.is_debug_port_available(debug_port):
                logger.debug("Browser is ready for connections")
                return True
            
            await asyncio.sleep(0.5)
        
        logger.error(f"Browser did not become ready within {timeout} seconds")
        return False
    
    async def _connect_playwright(self, debug_port: int) -> bool:
        """Connect to the browser using Playwright."""
        try:
            self._playwright = await async_playwright().start()
            
            
            browser_type = self._get_playwright_browser_type()
            
            
            self._browser = await browser_type.connect_over_cdp(f"http://localhost:{debug_port}")
            
            
            contexts = self._browser.contexts
            if contexts:
                self._context = contexts[0]
                logger.debug("Using existing browser context")
            else:
                self._context = await self._browser.new_context()
                logger.debug("Created new browser context")
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting with Playwright: {e}")
            return False
    
    def _get_playwright_browser_type(self):
        """Get the appropriate Playwright browser type."""
        if self.config.browser_name in [BrowserType.CHROME, BrowserType.CHROMIUM, BrowserType.EDGE, BrowserType.BRAVE]:
            return self._playwright.chromium
        elif self.config.browser_name == BrowserType.FIREFOX:
            return self._playwright.firefox
        elif self.config.browser_name == BrowserType.SAFARI:
            return self._playwright.webkit
        else:
            
            return self._playwright.chromium 