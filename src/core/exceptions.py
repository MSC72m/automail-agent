"""Custom exceptions for the automail agent application."""

from typing import Optional


class AutomailException(Exception):
    """Base exception for automail agent errors."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class BrowserException(AutomailException):
    """Exception raised when browser operations fail."""
    
    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message, status_code)


class ProfileException(AutomailException):
    """Exception raised when profile operations fail."""
    
    def __init__(self, message: str, status_code: int = 404):
        super().__init__(message, status_code)


class EmailValidationException(AutomailException):
    """Exception raised when email validation fails."""
    
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code)


class GmailConnectionException(AutomailException):
    """Exception raised when Gmail connection fails."""
    
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message, status_code)


class EmailSendException(AutomailException):
    """Exception raised when email sending fails."""
    
    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message, status_code)


class BrowserLaunchException(BrowserException):
    """Exception raised when browser fails to launch."""
    
    def __init__(self, message: str = "Failed to launch browser"):
        super().__init__(message, 503)


class BrowserPageException(BrowserException):
    """Exception raised when browser page operations fail."""
    
    def __init__(self, message: str = "Failed to get browser page"):
        super().__init__(message, 503) 