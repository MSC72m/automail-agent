import asyncio
import logging
from datetime import datetime
from typing import Optional
import uuid

from src.api.services.interfaces.email_interface import EmailServiceInterface
from src.schemas.email import EmailRequest, EmailResponse
from src.schemas.browser import BrowserConfig
from src.schemas.email import EmailInput
from src.schemas.enums import BrowserType
from src.browser.mailer import GmailMailer

logger = logging.getLogger(__name__)

class EmailService(EmailServiceInterface):
    """Email service implementation using Gmail mailer"""
    
    def __init__(self):
        self._email_history = {}  
    
    async def send_email(self, email_request: EmailRequest, headless: bool = True, browser_config: Optional[BrowserConfig] = None) -> EmailResponse:
        """Send an email using Gmail mailer"""
        try:
            
            email_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            
            if browser_config is None:
                browser_config = BrowserConfig(
                    browser_name=BrowserType.CHROME,
                    headless=headless
                )
            
            
            email_input = EmailInput(
                to=str(email_request.to),
                subject=email_request.subject,
                body=email_request.body,
                attachments=email_request.attachments
            )
            
            
            self._email_history[email_id] = {
                "status": "sending",
                "timestamp": timestamp,
                "request": email_request.dict()
            }
            
            
            mailer = GmailMailer(browser_config)
            
            try:
                
                connected = await mailer.connect_to_gmail()
                if not connected:
                    self._email_history[email_id]["status"] = "failed"
                    return EmailResponse(
                        success=False,
                        message="Failed to connect to Gmail",
                        email_id=email_id,
                        timestamp=timestamp
                    )
                
                
                success = await mailer.send_email(email_input)
                
                if success:
                    self._email_history[email_id]["status"] = "sent"
                    return EmailResponse(
                        success=True,
                        message="Email sent successfully",
                        email_id=email_id,
                        timestamp=timestamp
                    )
                else:
                    self._email_history[email_id]["status"] = "failed"
                    return EmailResponse(
                        success=False,
                        message="Failed to send email through Gmail interface",
                        email_id=email_id,
                        timestamp=timestamp
                    )
                    
            finally:
                
                await mailer.close()
                
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            self._email_history[email_id]["status"] = "error"
            return EmailResponse(
                success=False,
                message=f"Error sending email: {str(e)}",
                email_id=email_id,
                timestamp=timestamp
            )
    
    async def validate_email_format(self, email_request: EmailRequest) -> bool:
        """Validate email format and content"""
        try:
            
            if not email_request.to or not email_request.subject or not email_request.body:
                return False
            
            
            if len(email_request.subject.strip()) == 0:
                return False
                
            if len(email_request.body.strip()) == 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating email: {e}")
            return False
    
    async def get_email_status(self, email_id: str) -> Optional[str]:
        """Get the status of a sent email"""
        try:
            if email_id in self._email_history:
                return self._email_history[email_id]["status"]
            return None
        except Exception as e:
            logger.error(f"Error getting email status: {e}")
            return None 