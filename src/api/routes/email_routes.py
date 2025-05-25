from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List, Dict, Any
import json

from src.schemas.email import EmailRequest, EmailResponse, EmailPriority
from src.api.services.email_service import EmailService
from src.api.services.profile_service import ProfileService
from src.schemas.enums import BrowserType

router = APIRouter(prefix="/email", tags=["email"])

def get_email_service() -> EmailService:
    return EmailService()

def get_profile_service() -> ProfileService:
    return ProfileService()

@router.post("/send", response_model=EmailResponse)
async def send_email(
    to: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    priority: EmailPriority = Form(EmailPriority.NORMAL),
    profile_name: Optional[str] = Form(None),
    attachments: Optional[str] = Form(None),
    headless: bool = Form(True),
    email_service: EmailService = Depends(get_email_service),
    profile_service: ProfileService = Depends(get_profile_service)
) -> EmailResponse:
    """Send an email through Gmail web interface"""
    try:
        attachment_list = []
        if attachments and attachments.strip():
            attachment_list = [path.strip() for path in attachments.split(',') if path.strip()]
        
        email_request = EmailRequest(
            to=to,
            subject=subject,
            body=body,
            priority=priority,
            profile_name=profile_name if profile_name else None,
            attachments=attachment_list
        )
        
        is_valid = await email_service.validate_email_format(email_request)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        
        if email_request.profile_name:
            profile_exists = await profile_service.validate_profile_exists(
                email_request.profile_name, 
                BrowserType.CHROME
            )
            if not profile_exists:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Profile '{email_request.profile_name}' not found"
                )
        
        response = await email_service.send_email(email_request, headless=headless)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/status/{email_id}")
async def get_email_status(
    email_id: str,
    email_service: EmailService = Depends(get_email_service)
) -> Dict[str, Any]:
    """Get the status of a sent email"""
    try:
        status = await email_service.get_email_status(email_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Email not found")
        
        return {"email_id": email_id, "status": status}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/validate")
async def validate_email(
    email_request: EmailRequest,
    email_service: EmailService = Depends(get_email_service)
) -> Dict[str, bool]:
    """Validate email format and content"""
    try:
        is_valid = await email_service.validate_email_format(email_request)
        return {"valid": is_valid}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 