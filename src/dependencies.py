from src.services.email_service import EmailService
from src.services.profile_service import ProfileService
from src.schemas.browser import BrowserConfig
from src.schemas.enums import BrowserType
from src.utils.logger import get_logger

logger = get_logger(__name__)

def get_email_service() -> EmailService:
    """Dependency injection for EmailService.
    
    Returns:
        EmailService: Configured email service instance
    """
    return EmailService()


def get_profile_service() -> ProfileService:
    """Dependency injection for ProfileService.
    
    Returns:
        ProfileService: Configured profile service instance
    """
    # Default browser config for profile service
    default_config = BrowserConfig(
        browser_name=BrowserType.CHROME,
        headless=False
    )
    return ProfileService(default_config)



