"""
Logging utilities for AutoMail Agent.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Set level
        log_level = level or "INFO"
        logger.setLevel(getattr(logging, log_level.upper()))
    
    return logger

# Default logger for the application
default_logger = get_logger(
    name="automail",
    level="DEBUG"
) 