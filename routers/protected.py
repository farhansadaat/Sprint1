from fastapi import APIRouter, Depends
from typing import Dict

from dependencies.auth import get_current_user

router = APIRouter()


@router.get("/profile")
async def get_profile(current_user: Dict[str, str] = Depends(get_current_user)):
    """
    Get the current user's profile.
    """
    return {
        "user_id": current_user["user_id"],
        "bio": "Sample bio"  # Mock data
    }


@router.get("/jobs")
async def get_jobs(current_user: Dict[str, str] = Depends(get_current_user)):
    """
    Get the user's jobs.
    """
    return {
        "user_id": current_user["user_id"],
        "jobs": ["Job 1", "Job 2"]  # Mock data
    }


@router.post("/jobs")
async def create_job(current_user: Dict[str, str] = Depends(get_current_user)):
    """
    Create a new job for the user.
    """
    return {
        "user_id": current_user["user_id"],
        "message": "Job created successfully"
    }