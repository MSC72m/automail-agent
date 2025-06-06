import logging
import sys
import os
from pathlib import Path
from typing import Optional, Dict

from src.schemas.config import config

class LoggerManager:
    """Manages logger configuration and state."""
    
    def __init__(self):
        self._loggers: Dict[str, logging.Logger] = {}
        self._setup_complete = False
    
    def setup_logging(self) -> None:
        """Setup logging configuration."""
        if self._setup_complete:
            return
        
        # Import config here to avoid circular imports
            
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(config.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "automail.log")
        
        logging.basicConfig(
            level=getattr(logging, config.log_level.value),
            format=config.log_format,
            datefmt=config.log_date_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_file, encoding='utf-8')
            ],
            force=True  
        )
        
        self._setup_complete = True
    
    def get_logger(self, name: str, level: Optional[str] = None) -> logging.Logger:
        """Get a configured logger instance.
        
        Args:
            name: Logger name (usually __name__)
            level: Optional override for log level
            
        Returns:
            Configured logger instance
        """
        if not self._setup_complete:
            self.setup_logging()
            
        if name not in self._loggers:
            logger = logging.getLogger(name)
            
            # Set custom level if provided
            if level:
                logger.setLevel(getattr(logging, level.upper()))
            
            self._loggers[name] = logger
        
        return self._loggers[name]


# Global logger manager instance
_logger_manager = LoggerManager()

# Convenience functions
def setup_logging() -> None:
    """Setup logging configuration."""
    _logger_manager.setup_logging()


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        level: Optional override for log level
        
    Returns:
        Configured logger instance
    """
    return _logger_manager.get_logger(name, level)

