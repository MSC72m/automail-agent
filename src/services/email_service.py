from datetime import datetime
from typing import Optional
import uuid

from src.services.interfaces.email_interface import EmailServiceInterface
from src.schemas.email import EmailRequest, EmailResponse
from src.schemas.browser import BrowserConfig
from src.schemas.email import EmailInput
from core.enums import BrowserType
from src.browser.mailer import GmailMailer
from src.core.logger import get_logger
from src.core.exceptions import (
    EmailValidationException,
    BrowserLaunchException, 
    BrowserPageException,
    GmailConnectionException,
    EmailSendException
)

logger = get_logger(__name__)

class EmailService(EmailServiceInterface):
    """Email service implementation using Gmail mailer"""
    
    def __init__(self):
        self._email_history = {}  
    
    async def send_email(self, email_request: EmailRequest, headless: bool = True, browser_config: Optional[BrowserConfig] = None) -> EmailResponse:
        """Send an email using Gmail mailer"""
        email_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        try:
            # Validate email before processing
            is_valid = await self.validate_email_format(email_request)
            if not is_valid:
                raise EmailValidationException("Invalid email format or missing required fields")
            
            # Set default browser config if not provided
            if browser_config is None:
                browser_config = BrowserConfig(
                    browser_name=BrowserType.CHROME,
                    headless=headless
                )
            
            # Create email input
            email_input = EmailInput(
                to=str(email_request.to),
                subject=email_request.subject,
                body=email_request.body
            )
            
            # Track email in history
            self._email_history[email_id] = {
                "status": "sending",
                "timestamp": timestamp,
                "request": email_request.dict()
            }
            
            # Initialize mailer
            mailer = GmailMailer(browser_config)
            
            try:
                # Launch browser
                profile_name = browser_config.profile_name if browser_config.profile_name else "Default"
                logger.info(f"Launching browser with profile: {profile_name}")
                
                connected = await mailer.launcher.launch(profile_name=profile_name)
                if not connected:
                    self._email_history[email_id]["status"] = "failed"
                    raise BrowserLaunchException(f"Failed to launch browser with profile: {profile_name}")
                
                # Get browser page
                mailer.page = await mailer.launcher.get_page()
                if not mailer.page:
                    self._email_history[email_id]["status"] = "failed"
                    raise BrowserPageException("Failed to get browser page")
                
                # Connect to Gmail
                gmail_connected = await mailer.connect_to_gmail()
                if not gmail_connected:
                    self._email_history[email_id]["status"] = "failed"
                    raise GmailConnectionException("Failed to connect to Gmail. Please check your credentials or network connection.")
                
                # Send email
                success = await mailer.send_email(email_input)
                
                if not success:
                    self._email_history[email_id]["status"] = "failed"
                    raise EmailSendException("Failed to send email through Gmail interface. Please check recipient address and try again.")
                
                # Success case
                self._email_history[email_id]["status"] = "sent"
                logger.info(f"Email sent successfully to {email_request.to}")
                
                return EmailResponse(
                    success=True,
                    message="Email sent successfully",
                    email_id=email_id,
                    timestamp=timestamp
                )
                    
            finally:
                await mailer.terminate()
                
        except (EmailValidationException, BrowserLaunchException, BrowserPageException, 
                GmailConnectionException, EmailSendException) as e:
            # Re-raise custom exceptions to be handled by route handler
            self._email_history[email_id]["status"] = "error"
            logger.error(f"Email service error: {e}")
            raise
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error sending email: {e}")
            self._email_history[email_id]["status"] = "error"
            raise EmailSendException(f"Unexpected error occurred while sending email: {str(e)}")
    
    async def validate_email_format(self, email_request: EmailRequest) -> bool:
        """Validate email format and content"""
        try:
            # Check for required fields
            if not email_request.to or not email_request.subject or not email_request.body:
                return False
            
            # Check for empty strings after stripping whitespace
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