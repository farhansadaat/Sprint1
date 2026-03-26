import base64
from typing import Optional

from passlib.context import CryptContext

from .token_blacklist import TokenBlacklist

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """Create a simple base64-encoded access token."""
    user_id = data.get("sub")
    if user_id is None:
        raise ValueError("user_id required")
    token_data = f"{user_id}"
    encoded_token = base64.b64encode(token_data.encode()).decode()
    return encoded_token


def verify_token(token: str, blacklist: TokenBlacklist) -> Optional[int]:
    """
    Verify a base64-encoded token and check if it's blacklisted.

    Returns the user_id if valid and not blacklisted, None otherwise.
    """
    if blacklist.is_blacklisted(token):
        return None

    try:
        decoded_data = base64.b64decode(token).decode()
        user_id = int(decoded_data)
        return user_id
    except (ValueError, base64.binascii.Error):
        return None