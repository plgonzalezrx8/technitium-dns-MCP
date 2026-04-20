class TechnitiumApiError(Exception):
    """Base error for Technitium API failures."""


class InvalidTokenError(TechnitiumApiError):
    """Raised when Technitium rejects the configured token."""
