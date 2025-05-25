"""
Browser automation module for AutoMail Agent.

This module provides a simplified browser automation system for Chrome and Firefox
on Windows and Linux only. It focuses on profile copying and automation setup.

Main Components:
- BrowserLauncher: Main orchestrator for browser automation
- BrowserConfig: Configuration for browser settings
- Profile managers for Chrome and Firefox

Example Usage:
    from src.browser import BrowserLauncher
    from src.schemas.browser import BrowserConfig
    from src.schemas.enums import BrowserType
    
    config = BrowserConfig(
        browser_name=BrowserType.CHROME,
        headless=False
    )
    
    launcher = BrowserLauncher(config)
    success = await launcher.launch()
    
    if success:
        page = await launcher.get_page()
        await page.goto("https://example.com")
        
        await launcher.close()
"""

from src.browser.launchers import BrowserLauncher
from src.browser.interfaces import (
    IBrowserProfileManager
)
from src.browser.profile_managers import (
    BaseBrowserProfileManager,
    ChromeProfileManager,
    FirefoxProfileManager,
    DefaultProfileManager,
    ProfileManagerFactory,
)

__all__ = [
    "BrowserLauncher",
    "IBrowserProfileManager",
    "ProfileManagerFactory",
    "BaseBrowserProfileManager",
    "ChromeProfileManager",
    "FirefoxProfileManager",
    "DefaultProfileManager",
]