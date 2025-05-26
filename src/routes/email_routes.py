from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from typing import Optional, List
import os

from src.services.email_service import EmailService
from src.services.profile_service import ProfileService
from src.schemas.email import EmailRequest, EmailResponse
from src.schemas.browser import BrowserConfig
from src.schemas.enums import BrowserType
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
email_service = EmailService()
profile_service = ProfileService()

@router.post("/send-email", response_model=EmailResponse)
async def send_email(
    to: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    headless: str = Form("true"),  
    browser_name: str = Form("chrome"),
    profile_name: Optional[str] = Form(None)
) -> EmailResponse:
    """Send an email via Gmail web interface."""
    try:
        
        headless_bool = headless.lower() == "true"
        
        logger.info(f"Sending email to {to} with subject: {subject}, headless: {headless_bool}, profile: {profile_name}")
        
        
        if headless_bool and (not profile_name or profile_name.strip() == ""):
            raise HTTPException(
                status_code=400, 
                detail="A specific profile must be selected when using headless mode. Default Profile is only available for non-headless mode."
            )
        
        
        email_request = EmailRequest(
            to=to,
            subject=subject,
            body=body,
            profile_name=profile_name
        )
        
        
        browser_config = BrowserConfig(
            browser_name=BrowserType(browser_name.lower()),
            headless=headless_bool,
            profile_name=profile_name
        )
        
        
        response = await email_service.send_email(
            email_request=email_request,
            headless=headless_bool,
            browser_config=browser_config
        )
        
        
        if response.success:
            logger.info(f"Email sent successfully to {to}")
        else:
            logger.error(f"Failed to send email to {to}: {response.message}")
        
        return response
            
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

@router.get("/profiles/{browser_name}")
async def get_profiles(browser_name: str) -> dict:
    """Get available browser profiles for the specified browser."""
    try:
        logger.info(f"Getting profiles for browser: {browser_name}")
        
        
        try:
            browser_type = BrowserType(browser_name.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid browser name: {browser_name}")
        
        profiles_response = await profile_service.get_available_profiles(browser_type)
        profile_names = [profile.name for profile in profiles_response.profiles]
        logger.info(f"Found {len(profile_names)} profiles for {browser_name}")
        
        return {
            "browser": browser_name,
            "profiles": profile_names
        }
        
    except Exception as e:
        logger.error(f"Error getting profiles for {browser_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting profiles: {str(e)}")

@router.get("/email-status/{email_id}")
async def get_email_status(email_id: str) -> dict:
    """Get the status of a sent email."""
    try:
        status = email_service.get_email_status(email_id)
        if status:
            return status
        else:
            raise HTTPException(status_code=404, detail="Email not found")
    except Exception as e:
        logger.error(f"Error getting email status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting email status: {str(e)}")

@router.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static files."""
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    file_full_path = os.path.join(static_dir, file_path)
    
    if os.path.exists(file_full_path) and os.path.isfile(file_full_path):
        return FileResponse(file_full_path)
    else:
        raise HTTPException(status_code=404, detail="File not found") 