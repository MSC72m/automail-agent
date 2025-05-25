"""
Browser automation module for AutoMail Agent.

This module provides a clean, modular architecture for browser automation
using the Strategy pattern. It supports multiple browsers (Chrome, Chromium,
Edge, Brave, Firefox) across different operating systems.

Main Components:
- BrowserLauncher: Main orchestrator for browser automation
- BrowserConfig: Configuration for browser settings
- Various strategy implementations for different browsers and platforms

Example Usage:
    from src.browser import BrowserLauncher
    from src.schemas.browser import BrowserConfig
    from src.schemas.enums import BrowserType
    
    
    config = BrowserConfig(
        browser_name=BrowserType.CHROME,
        headless=False
    )
    
    
    launcher = BrowserLauncher(config)
    success = await launcher.launch(profile_name="MyProfile")
    
    if success:
        page = await launcher.get_page()
        await page.goto("https://example.com")
        
        
        await launcher.close()
"""

from src.browser.launchers import BrowserLauncher
from src.browser.interfaces import (
    IBrowserFinder,
    IBrowserProfileManager, 
    IBrowserProcessManager,
    IBrowserLauncher
)
from src.browser.finders import (
    BrowserFinderFactory,
    ChromeFinder,
    EdgeFinder,
    BraveFinder,
    FirefoxFinder,
    AutoFinder
)
from src.browser.profile_managers import (
    BaseBrowserProfileManager,
    ChromiumBasedProfileManager,
    FirefoxProfileManager,
    ChromeProfileManager,
    EdgeProfileManager,
    BraveProfileManager,
    DefaultProfileManager,
    ProfileManagerFactory,
)
from src.browser.process_managers import (
    BrowserProcessManagerFactory,
    ChromiumBasedProcessManager,
    FirefoxProcessManager
)

__all__ = [
    "BrowserLauncher",
    "IBrowserFinder",
    "IBrowserProfileManager", 
    "IBrowserProcessManager",
    "IBrowserLauncher",
    "BrowserFinderFactory",
    "ChromeFinder",
    "EdgeFinder", 
    "BraveFinder",
    "FirefoxFinder",
    "AutoFinder",
    "ProfileManagerFactory",
    "BrowserProcessManagerFactory",
    "BaseBrowserProfileManager",
    "ChromiumBasedProfileManager",
    "FirefoxProfileManager",
    "ChromeProfileManager",
    "EdgeProfileManager",
    "BraveProfileManager",
    "DefaultProfileManager",
    "ChromiumBasedProcessManager",
    "FirefoxProcessManager",
]