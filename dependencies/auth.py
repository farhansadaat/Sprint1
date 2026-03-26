from typing import Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from utils.security import verify_token
from utils.token_blacklist import TokenBlacklist

security = HTTPBearer(auto_error=False)

# Global blacklist instance (in production, use dependency injection or database)
blacklist = TokenBlacklist()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, str]:
    """
    Dependency to get the current authenticated user.

    Returns a dict with user info including token.
    Raises HTTPException if authentication fails.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    token = credentials.credentials
    user_id = verify_token(token, blacklist)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return {"user_id": user_id, "token": token}