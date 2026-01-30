"""
OG Pilot Python SDK

A Python client for generating OG Pilot Open Graph images via signed JWTs.
"""

from typing import Any

from og_pilot.client import Client
from og_pilot.config import Configuration
from og_pilot.exceptions import ConfigurationError, OgPilotError, RequestError

__version__ = "0.1.1"
__all__ = [
    "Client",
    "Configuration",
    "OgPilotError",
    "ConfigurationError",
    "RequestError",
    "configure",
    "reset_config",
    "get_config",
    "client",
    "create_client",
    "create_image",
]

# Global configuration instance
_config: Configuration | None = None


def get_config() -> Configuration:
    """Get the global configuration, creating it if necessary."""
    global _config
    if _config is None:
        _config = Configuration()
    return _config


def configure(**kwargs: Any) -> Configuration:
    """
    Configure the global OG Pilot client.

    Args:
        api_key: Your OG Pilot API key
        domain: Your domain registered with OG Pilot
        base_url: OG Pilot API base URL (default: https://ogpilot.com)
        open_timeout: Connection timeout in seconds (default: 5)
        read_timeout: Read timeout in seconds (default: 10)

    Returns:
        The updated Configuration instance

    Example:
        >>> import og_pilot
        >>> og_pilot.configure(
        ...     api_key="your-api-key",
        ...     domain="example.com"
        ... )
    """
    global _config
    if _config is None:
        _config = Configuration(**kwargs)
    else:
        for key, value in kwargs.items():
            if hasattr(_config, key):
                setattr(_config, key, value)
    return _config


def reset_config() -> None:
    """Reset the global configuration to defaults."""
    global _config
    _config = None


def client() -> Client:
    """Get a client instance using the global configuration."""
    return Client(get_config())


def create_client(**kwargs: Any) -> Client:
    """
    Create a new client with custom configuration.

    Args:
        api_key: Your OG Pilot API key
        domain: Your domain registered with OG Pilot
        base_url: OG Pilot API base URL
        open_timeout: Connection timeout in seconds
        read_timeout: Read timeout in seconds

    Returns:
        A new Client instance

    Example:
        >>> from og_pilot import create_client
        >>> client = create_client(
        ...     api_key="your-api-key",
        ...     domain="example.com"
        ... )
    """
    config = Configuration(**kwargs)
    return Client(config)


def create_image(
    params: dict[str, Any] | None = None,
    *,
    json_response: bool = False,
    iat: int | float | None = None,
    headers: dict[str, str] | None = None,
    **kwargs: Any,
) -> str | dict[str, Any]:
    """
    Generate an OG Pilot image URL using the global configuration.

    Args:
        params: Dictionary of template parameters
        json_response: If True, return JSON metadata instead of URL
        iat: Issue time for cache busting (Unix timestamp or datetime)
        headers: Additional HTTP headers
        **kwargs: Additional template parameters (merged with params)

    Returns:
        Image URL string or JSON metadata dict if json_response=True

    Example:
        >>> import og_pilot
        >>> og_pilot.configure(api_key="...", domain="example.com")
        >>> url = og_pilot.create_image(
        ...     template="blog_post",
        ...     title="My Blog Post",
        ...     description="A great article"
        ... )
    """
    merged_params = {**(params or {}), **kwargs}
    return client().create_image(merged_params, json_response=json_response, iat=iat, headers=headers)
