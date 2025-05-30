from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from src.schemas.profile import ProfileListResponse, BrowserProfile
from src.services.profile_service import ProfileService
from src.schemas.enums import BrowserType
from src.dependencies import get_profile_service

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/", response_model=ProfileListResponse)
async def get_profiles(
    browser_type: Optional[BrowserType] = Query(None, description="Filter by browser type"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get list of available browser profiles"""
    try:
        profiles = await profile_service.get_available_profiles(browser_type)
        return profiles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{browser_type}/{profile_name}", response_model=BrowserProfile)
async def get_profile_by_name(
    browser_type: BrowserType,
    profile_name: str,
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get a specific profile by name and browser type"""
    try:
        profile = await profile_service.get_profile_by_name(profile_name, browser_type)
        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{browser_type}/default", response_model=BrowserProfile)
async def get_default_profile(
    browser_type: BrowserType,
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get the default profile for a browser type"""
    try:
        profile = await profile_service.get_default_profile(browser_type)
        if profile is None:
            raise HTTPException(status_code=404, detail="No default profile found")
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{browser_type}/{profile_name}/validate")
async def validate_profile(
    browser_type: BrowserType,
    profile_name: str,
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Validate if a profile exists"""
    try:
        exists = await profile_service.validate_profile_exists(profile_name, browser_type)
        return {"exists": exists, "profile_name": profile_name, "browser_type": browser_type}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 