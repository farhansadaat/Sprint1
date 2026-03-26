import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from dependencies.auth import blacklist
from routers.auth import router as auth_router
from routers.jobs import router as jobs_router

app = FastAPI()
app.include_router(auth_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_mock_jobs():
    """Reset mock jobs before each test."""
    from routers.jobs import mock_jobs
    mock_jobs.clear()
    mock_jobs.extend([
        {"id": 1, "title": "Job 1", "description": "Desc 1", "user_id": 1},
        {"id": 2, "title": "Job 2", "description": "Desc 2", "user_id": 1},
        {"id": 3, "title": "Job 3", "description": "Desc 3", "user_id": 2},
    ])
    yield


def login_as_user(user_id: int):
    """Helper to login as a user and get token."""
    username = "testuser" if user_id == 1 else "testuser2"
    login_data = {"username": username, "password": "testpass"}
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


def test_user_can_access_own_jobs():
    """Test that user can access their own jobs."""
    token = login_as_user(1)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/jobs", headers=headers)
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) == 2  # user 1 has 2 jobs
    assert all(job["user_id"] == 1 for job in jobs)


def test_user_can_access_own_job_detail():
    """Test that user can access their own job detail."""
    token = login_as_user(1)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/jobs/1", headers=headers)
    assert response.status_code == 200
    job = response.json()
    assert job["id"] == 1
    assert job["user_id"] == 1


def test_user_cannot_access_other_users_job():
    """Test that user cannot access another user's job."""
    token = login_as_user(1)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/jobs/3", headers=headers)  # job 3 belongs to user 2
    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have access to this resource"}


def test_user_cannot_update_other_users_job():
    """Test that user cannot update another user's job."""
    token = login_as_user(1)
    headers = {"Authorization": f"Bearer {token}"}

    update_data = {"title": "Updated", "description": "Updated desc"}
    response = client.put("/api/jobs/3", json=update_data, headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have access to this resource"}


def test_user_cannot_delete_other_users_job():
    """Test that user cannot delete another user's job."""
    token = login_as_user(1)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/api/jobs/3", headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have access to this resource"}


def test_user_can_update_own_job():
    """Test that user can update their own job."""
    token = login_as_user(1)
    headers = {"Authorization": f"Bearer {token}"}

    update_data = {"title": "Updated Job 1", "description": "Updated desc"}
    response = client.put("/api/jobs/1", json=update_data, headers=headers)
    assert response.status_code == 200
    job = response.json()
    assert job["title"] == "Updated Job 1"
    assert job["user_id"] == 1


def test_user_can_delete_own_job():
    """Test that user can delete their own job."""
    token = login_as_user(1)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/api/jobs/1", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Job deleted successfully"}

    # Verify it's deleted
    response = client.get("/api/jobs/1", headers=headers)
    assert response.status_code == 404


def test_access_non_existent_job():
    """Test access to non-existent job."""
    token = login_as_user(1)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/jobs/999", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}


def test_user_can_create_job():
    """Test that user can create a job."""
    token = login_as_user(1)
    headers = {"Authorization": f"Bearer {token}"}

    create_data = {"title": "New Job", "description": "New desc"}
    response = client.post("/api/jobs", json=create_data, headers=headers)
    assert response.status_code == 200
    job = response.json()
    assert job["title"] == "New Job"
    assert job["user_id"] == 1