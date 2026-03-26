from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List
from pydantic import BaseModel

from dependencies.auth import get_current_user

router = APIRouter()

# Mock data for demonstration
mock_jobs = [
    {"id": 1, "title": "Job 1", "description": "Desc 1", "user_id": 1},
    {"id": 2, "title": "Job 2", "description": "Desc 2", "user_id": 1},
    {"id": 3, "title": "Job 3", "description": "Desc 3", "user_id": 2},
]


class JobCreate(BaseModel):
    title: str
    description: str


class JobUpdate(BaseModel):
    title: str
    description: str


@router.get("/jobs", response_model=List[Dict])
async def get_jobs(current_user: Dict = Depends(get_current_user)):
    """
    Get all jobs for the current user.
    """
    user_jobs = [job for job in mock_jobs if job["user_id"] == current_user["user_id"]]
    return user_jobs


@router.get("/jobs/{job_id}")
async def get_job(job_id: int, current_user: Dict = Depends(get_current_user)):
    """
    Get a specific job if owned by the current user.
    """
    job = next((j for j in mock_jobs if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["user_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this resource"
        )
    return job


@router.post("/jobs")
async def create_job(job_data: JobCreate, current_user: Dict = Depends(get_current_user)):
    """
    Create a new job for the current user.
    """
    new_id = max(j["id"] for j in mock_jobs) + 1 if mock_jobs else 1
    new_job = {
        "id": new_id,
        "title": job_data.title,
        "description": job_data.description,
        "user_id": current_user["user_id"]
    }
    mock_jobs.append(new_job)
    return new_job


@router.put("/jobs/{job_id}")
async def update_job(job_id: int, job_data: JobUpdate, current_user: Dict = Depends(get_current_user)):
    """
    Update a job if owned by the current user.
    """
    job = next((j for j in mock_jobs if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["user_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this resource"
        )
    job["title"] = job_data.title
    job["description"] = job_data.description
    return job


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: int, current_user: Dict = Depends(get_current_user)):
    """
    Delete a job if owned by the current user.
    """
    job = next((j for j in mock_jobs if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["user_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this resource"
        )
    mock_jobs.remove(job)
    return {"message": "Job deleted successfully"}