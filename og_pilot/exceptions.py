"""
OG Pilot Exceptions

Custom exceptions for the OG Pilot SDK.
"""


class OgPilotError(Exception):
    """Base exception for all OG Pilot errors."""

    pass


class ConfigurationError(OgPilotError):
    """Raised when there's a configuration problem."""

    pass


class RequestError(OgPilotError):
    """Raised when an API request fails."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code
