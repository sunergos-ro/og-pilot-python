"""
OG Pilot Configuration

Configuration management for the OG Pilot SDK.
"""

import os
from dataclasses import dataclass, field

DEFAULT_BASE_URL = "https://ogpilot.com"


@dataclass
class Configuration:
    """
    Configuration for the OG Pilot client.

    Attributes:
        api_key: Your OG Pilot API key. Defaults to OG_PILOT_API_KEY env var.
        domain: Your domain registered with OG Pilot. Defaults to OG_PILOT_DOMAIN env var.
        base_url: OG Pilot API base URL. Defaults to https://ogpilot.com.
        open_timeout: Connection timeout in seconds. Defaults to 5.
        read_timeout: Read timeout in seconds. Defaults to 10.
    """

    api_key: str | None = field(default_factory=lambda: os.environ.get("OG_PILOT_API_KEY"))
    domain: str | None = field(default_factory=lambda: os.environ.get("OG_PILOT_DOMAIN"))
    base_url: str = DEFAULT_BASE_URL
    open_timeout: float = 5.0
    read_timeout: float = 10.0
