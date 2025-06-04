"""
WSL Helper Utilities

This module provides utilities for detecting and configuring WSL-specific settings.
"""

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


def find_available_windows_browsers() -> Dict[str, str]:
    """
    Find available Windows browsers when running under WSL.
    
    Returns:
        Dict[str, str]: Dictionary mapping browser names to their executable paths
    """
    available_browsers = {}
    
    if not is_wsl():
        return available_browsers
    
    browser_paths = get_windows_browser_paths()
    
    for browser_name, paths in browser_paths.items():
        for path in paths:
            if os.path.exists(path):
                available_browsers[browser_name] = path
                logger.info(f"Found Windows {browser_name}: {path}")
                break
    
    return available_browsers


def find_available_windows_profiles() -> Dict[str, str]:
    """
    Find available Windows browser profiles when running under WSL.
    
    Returns:
        Dict[str, str]: Dictionary mapping browser names to their profile paths
    """
    available_profiles = {}
    
    if not is_wsl():
        return available_profiles
    
    username = get_windows_username()
    if not username:
        logger.warning("Could not determine Windows username")
        return available_profiles
    
    profile_paths = get_windows_profile_paths(username)
    
    for browser_name, path in profile_paths.items():
        if os.path.exists(path):
            available_profiles[browser_name] = path
            logger.info(f"Found Windows {browser_name} profile: {path}")
    
    return available_profiles


def get_wsl_host_ip() -> Optional[str]:
    """
    Get the WSL host IP address for accessing Windows services.
    
    Returns:
        Optional[str]: Host IP address or None if not available
    """
    if not is_wsl():
        return None
    
    try:
        # Try to get host IP from /etc/resolv.conf
        with open('/etc/resolv.conf', 'r') as f:
            for line in f:
                if line.startswith('nameserver'):
                    ip = line.split()[1]
                    if ip and ip != '127.0.0.1':
                        return ip
    except Exception as e:
        logger.debug(f"Error reading /etc/resolv.conf: {e}")
    
    return None


def configure_wsl_environment() -> Dict[str, str]:
    """
    Configure environment variables for WSL.
    
    Returns:
        Dict[str, str]: Dictionary of environment variables to set
    """
    env_vars = {}
    
    if is_wsl():
        env_vars['IS_WSL'] = 'true'
        
        # Set Windows username if available
        username = get_windows_username()
        if username:
            env_vars['WINDOWS_USER'] = username
        
        # Set host IP if available
        host_ip = get_wsl_host_ip()
        if host_ip:
            env_vars['WSL_HOST_IP'] = host_ip
        
        # Configure display for X11 forwarding
        if not os.environ.get('DISPLAY'):
            env_vars['DISPLAY'] = ':0'
        
        logger.info("WSL environment configured")
    else:
        env_vars['IS_WSL'] = 'false'
    
    return env_vars


def get_wsl_info() -> Dict[str, any]:
    """
    Get comprehensive WSL environment information.
    
    Returns:
        Dict[str, any]: Dictionary containing WSL environment details
    """
    info = {
        'is_wsl': is_wsl(),
        'platform': platform.system(),
        'platform_release': platform.release(),
    }
    
    if info['is_wsl']:
        info.update({
            'windows_username': get_windows_username(),
            'host_ip': get_wsl_host_ip(),
            'available_windows_browsers': find_available_windows_browsers(),
            'available_windows_profiles': find_available_windows_profiles(),
            'distro_name': os.environ.get('WSL_DISTRO_NAME'),
        })
    
    return info 