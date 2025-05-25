"""
Browser interfaces and abstract base classes for the AutoMail Agent.

This module defines the contracts for browser-related operations using the Strategy pattern.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from playwright.async_api import Browser, BrowserContext, Page

from src.schemas.browser import BrowserConfig


class IBrowserFinder(ABC):
    """Interface for finding browser executables on different operating systems."""
    
    @abstractmethod
    def find_executable(self) -> Optional[str]:
        """Find the browser executable path."""
        pass


class IBrowserProfileManager(ABC):
    """Interface for managing browser profiles."""
    
    @abstractmethod
    def get_available_profiles(self) -> List[str]:
        """Get list of available browser profiles."""
        pass
    
    @abstractmethod
    def get_profile_path(self, profile_name: str) -> Optional[str]:
        """Get the path to a specific profile or default profile."""
        pass
    
    @abstractmethod
    def create_profile_if_needed(self, profile_name: str) -> str:
        """Create a profile if it doesn't exist and return its path."""
        pass


class IBrowserLauncher(ABC):
    """Interface for launching browsers with different configurations."""
    
    @abstractmethod
    async def launch(self, profile_name: str = "Default", debug_port: Optional[int] = None, 
                    additional_args: Optional[List[str]] = None) -> bool:
        """Launch the browser and return a page instance."""
        pass
    
    @abstractmethod
    async def connect_to_existing(self, debug_port: int) -> bool:
        """Connect to an existing browser instance if available."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the browser instance."""
        pass
    
    @abstractmethod
    async def terminate(self) -> None:
        """Forcefully terminate the browser process."""
        pass
    
    @abstractmethod
    async def get_page(self) -> Optional[Page]:
        pass
    
    @abstractmethod
    async def new_page(self) -> Optional[Page]:
        pass
    
    @abstractmethod
    def get_browser(self) -> Optional[Browser]:
        pass
    
    @abstractmethod
    def get_context(self) -> Optional[BrowserContext]:
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        pass


class IBrowserProcessManager(ABC):
    """Interface for managing browser processes."""
    
    @abstractmethod
    def is_debug_port_available(self, port: int) -> bool:
        """Check if the debug port is available."""
        pass
    
    @abstractmethod
    def kill_existing_instances(self, debug_port: Optional[int] = None) -> bool:
        """Kill existing browser instances."""
        pass
    
    @abstractmethod
    def launch_with_debug_port(self, executable_path: str, profile_path: str, 
                              debug_port: int, additional_args: Optional[List[str]] = None):
        """Launch browser with debug port enabled."""
        pass 