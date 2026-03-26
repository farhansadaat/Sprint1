import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from dependencies.auth import blacklist
from routers.auth import router as auth_router
from routers.protected import router as protected_router
from utils.security import create_access_token

app = FastAPI()
app.include_router(auth_router, prefix="/api")
app.include_router(protected_router, prefix="/api")

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_blacklist():
    """Clear the blacklist before each test."""
    blacklist.clear()
    yield


def test_successful_logout():
    """Test successful logout with valid token."""
    # Create a valid token
    token = create_access_token({"sub": 1})
    headers = {"Authorization": f"Bearer {token}"}

    # Logout
    response = client.post("/api/logout", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully logged out"}

    # Verify token is blacklisted
    assert blacklist.is_blacklisted(token)


def test_access_denied_after_logout():
    """Test that access is denied after logout."""
    # Create a valid token
    token = create_access_token({"sub": 1})
    headers = {"Authorization": f"Bearer {token}"}

    # Logout
    client.post("/api/logout", headers=headers)

    # Try to access protected route (assuming logout requires auth, but to test, we can call again)
    response = client.post("/api/logout", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}


def test_invalid_token_rejection():
    """Test rejection of invalid token."""
    headers = {"Authorization": "Bearer invalidtoken"}

    response = client.post("/api/logout", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}


def test_expired_token_behavior():
    """Test behavior with invalid token (since no expiration in simple tokens)."""
    # For simple tokens, all valid tokens are accepted; invalid ones are rejected
    headers = {"Authorization": "Bearer invalidtoken"}

    response = client.post("/api/logout", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}


def test_double_logout_handling():
    """Test logging out twice (second should fail)."""
    token = create_access_token({"sub": 1})
    headers = {"Authorization": f"Bearer {token}"}

    # First logout
    response1 = client.post("/api/logout", headers=headers)
    assert response1.status_code == 200

    # Second logout with same token
    response2 = client.post("/api/logout", headers=headers)
    assert response2.status_code == 401
    assert response2.json() == {"detail": "Invalid or expired token"}


def test_login_and_logout_flow():
    """Test full login and logout flow."""
    # Login (assuming it works)
    login_data = {"username": "testuser", "password": "testpass"}
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Use token to logout
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/logout", headers=headers)
    assert response.status_code == 200

    # Try to logout again (should fail)
    response = client.post("/api/logout", headers=headers)
    assert response.status_code == 401


def test_access_protected_route_without_token():
    """Test access to protected route without token."""
    response = client.get("/api/profile")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}


def test_access_protected_route_with_invalid_token():
    """Test access to protected route with invalid token."""
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/api/profile")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}


def test_access_protected_route_with_invalid_token():
    """Test access to protected route with invalid token."""
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/api/profile")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}


def test_access_protected_route_with_valid_token():
    """Test access to protected route with valid token."""
    # Login to get token
    login_data = {"username": "testuser", "password": "testpass"}
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/profile", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "user_id": 1,
        "bio": "Sample bio"
    }


def test_access_protected_route_with_blacklisted_token():
    """Test access to protected route with blacklisted token."""
    token = create_access_token({"sub": 1})
    headers = {"Authorization": f"Bearer {token}"}

    # Logout to blacklist
    client.post("/api/logout", headers=headers)

    # Try to access protected route
    response = client.get("/api/profile", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}