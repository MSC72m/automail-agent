from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from enum import Enum
from datetime import datetime

class EmailInput(BaseModel):
    """Email input model for browser automation"""
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")

class EmailRequest(BaseModel):
    """Email request model for API input"""
    to: EmailStr = Field(..., description="Recipient email address", example="recipient@example.com")
    subject: str = Field(..., min_length=1, max_length=200, description="Email subject", example="Important Meeting Tomorrow")
    body: str = Field(..., min_length=1, description="Email body content", example="Hi there,\n\nI hope this email finds you well. I wanted to reach out regarding our meeting scheduled for tomorrow at 2 PM.\n\nBest regards,\nJohn Doe")
    profile_name: Optional[str] = Field(default=None, description="Browser profile to use", example="default")

    @validator('body')
    def validate_body(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Email body cannot be empty')
        return v

class EmailResponse(BaseModel):
    """Email response model for API output"""
    success: bool = Field(..., description="Whether the email was sent successfully")
    message: str = Field(..., description="Response message")
    email_id: Optional[str] = Field(default=None, description="Email ID if available")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp of the operation")

class EmailStatus(BaseModel):
    """Email status model"""
    status: str = Field(..., description="Current status of the email")
    details: Optional[str] = Field(default=None, description="Additional status details") 