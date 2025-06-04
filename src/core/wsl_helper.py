import os
import platform
import subprocess
from pathlib import Path
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


def is_wsl() -> bool:
    """
    Detect if the current environment is running under WSL.
    
    Returns:
        bool: True if running under WSL, False otherwise
    """
    try:
        # Check /proc/version for WSL indicators
        if os.path.exists('/proc/version'):
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                return 'microsoft' in version_info or 'wsl' in version_info
        return 
    except Exception as e:
        logger.debug(f"Error checking /proc/version: {e}")
    
    # Fallback: check for WSL environment variables
    return os.environ.get('WSL_DISTRO_NAME') is not None


def get_windows_username() -> Optional[str]:
    """
    Get the Windows username when running under WSL.
    
    Returns:
        Optional[str]: Windows username or None if not available
    """
    if not is_wsl():
        return None
    
    try:
        # Try to get Windows username via cmd.exe
        result = subprocess.run(
            ['cmd.exe', '/c', 'echo %USERNAME%'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            username = result.stdout.strip()
            if username and username != '%USERNAME%':
                return username
    except Exception as e:
        logger.debug(f"Error getting Windows username: {e}")
    
    # Fallback: try environment variable
    return os.environ.get('WINDOWS_USER')


def get_windows_browser_paths() -> Dict[str, List[str]]:
    """
    Get common Windows browser installation paths.
    
    Returns:
        Dict[str, List[str]]: Dictionary mapping browser names to possible paths
    """
    return {
        'chrome': [
            '/mnt/c/Program Files/Google/Chrome/Application/chrome.exe',
            '/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe',
        ],
        'firefox': [
            '/mnt/c/Program Files/Mozilla Firefox/firefox.exe',
            '/mnt/c/Program Files (x86)/Mozilla Firefox/firefox.exe',
        ],
        'edge': [
            '/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
        ]
    }


def get_windows_profile_paths(username: str) -> Dict[str, str]:
    """
    Get Windows browser profile paths for a given username.
    
    Args:
        username (str): Windows username
        
    Returns:
        Dict[str, str]: Dictionary mapping browser names to profile paths
    """
    return {
        'chrome': f'/mnt/c/Users/{username}/AppData/Local/Google/Chrome/User Data',
        'firefox': f'/mnt/c/Users/{username}/AppData/Roaming/Mozilla/Firefox',
        'edge': f'/mnt/c/Users/{username}/AppData/Local/Microsoft/Edge/User Data',
    }

