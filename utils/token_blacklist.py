from typing import Set


class TokenBlacklist:
    """
    In-memory token blacklist for invalidated JWT tokens.
    This is a simple implementation using a set for fast lookups.
    In production, this should be replaced with a database-backed solution.
    """

    def __init__(self):
        self.blacklist: Set[str] = set()

    def add_token(self, token: str) -> None:
        """Add a token to the blacklist."""
        self.blacklist.add(token)

    def is_blacklisted(self, token: str) -> bool:
        """Check if a token is in the blacklist."""
        return token in self.blacklist

    def clear(self) -> None:
        """Clear all tokens from the blacklist (useful for testing or server restart)."""
        self.blacklist.clear()