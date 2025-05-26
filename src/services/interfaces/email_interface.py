from abc import ABC, abstractmethod
from typing import List, Optional
from src.schemas.email import EmailRequest, EmailResponse
from src.schemas.browser import BrowserConfig

class EmailServiceInterface(ABC):
    """Abstract interface for email services"""
    
    @abstractmethod
    async def send_email(self, email_request: EmailRequest, browser_config: Optional[BrowserConfig] = None) -> EmailResponse:
        """Send an email using the specified configuration"""
        pass
    
    @abstractmethod
    async def validate_email_format(self, email_request: EmailRequest) -> bool:
        """Validate email format and content"""
        pass
    
    @abstractmethod
    async def get_email_status(self, email_id: str) -> Optional[str]:
        """Get the status of a sent email"""
        pass 