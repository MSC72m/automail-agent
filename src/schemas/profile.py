from pydantic import BaseModel, Field
from typing import List, Optional

from src.core.enums import BrowserType

class BrowserProfile(BaseModel):
    """Browser profile model"""
    name: str = Field(..., description="Profile name", example="default")
    browser_type: BrowserType = Field(..., description="Browser type")
    path: str = Field(..., description="Profile directory path")
    is_default: bool = Field(default=False, description="Whether this is the default profile")
    description: Optional[str] = Field(default=None, description="Profile description")

class ProfileListResponse(BaseModel):
    """Response model for profile list"""
    profiles: List[BrowserProfile] = Field(..., description="List of available browser profiles")
    total_count: int = Field(..., description="Total number of profiles")

class ProfileRequest(BaseModel):
    """Request model for profile operations"""
    browser_type: BrowserType = Field(..., description="Browser type to use")
    headless: bool = Field(default=False, description="Whether to run in headless mode")
    profile_name: Optional[str] = Field(default=None, description="Specific profile name to use") 