"""
OG Pilot Client

HTTP client for the OG Pilot API.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING
from urllib.parse import urlencode, urljoin

import requests

from og_pilot import jwt_encoder
from og_pilot.exceptions import ConfigurationError, RequestError

if TYPE_CHECKING:
    from og_pilot.config import Configuration


ENDPOINT_PATH = "/api/v1/images"


class Client:
    """
    OG Pilot API client.

    Example:
        >>> from og_pilot import Client, Configuration
        >>> config = Configuration(api_key="...", domain="example.com")
        >>> client = Client(config)
        >>> url = client.create_image({"template": "default", "title": "Hello"})
    """

    def __init__(self, config: Configuration):
        """
        Initialize the client with configuration.

        Args:
            config: Configuration instance
        """
        self.config = config

    def create_image(
        self,
        params: dict | None = None,
        *,
        json_response: bool = False,
        iat: int | float | datetime | None = None,
        headers: dict[str, str] | None = None,
    ) -> str | dict:
        """
        Generate an OG Pilot image URL or fetch JSON metadata.

        Args:
            params: Dictionary of template parameters (must include 'title')
            json_response: If True, return JSON metadata instead of URL
            iat: Issue time for cache busting. Can be Unix timestamp (int/float)
                 or datetime object. If omitted, image is cached indefinitely.
            headers: Additional HTTP headers to send with the request

        Returns:
            Image URL string, or JSON metadata dict if json_response=True

        Raises:
            ConfigurationError: If API key or domain is missing
            RequestError: If the API request fails
            ValueError: If required parameters are missing
        """
        url = self._build_url(params or {}, iat)
        response = self._request(url, json_response=json_response, headers=headers or {})

        if json_response:
            return json.loads(response.text)

        # Return the redirect location or the final URL
        return response.headers.get("Location") or response.url or str(url)

    def _request(
        self,
        url: str,
        *,
        json_response: bool,
        headers: dict[str, str],
    ) -> requests.Response:
        """Make an HTTP request to the OG Pilot API."""
        request_headers = {}
        if json_response:
            request_headers["Accept"] = "application/json"
        request_headers.update(headers)

        timeout = (self.config.open_timeout, self.config.read_timeout)

        try:
            response = requests.get(
                url,
                headers=request_headers,
                timeout=timeout,
                allow_redirects=False,
            )

            if response.status_code >= 400:
                raise RequestError(
                    f"OG Pilot request failed with status {response.status_code}: {response.text}",
                    status_code=response.status_code,
                )

            return response

        except requests.exceptions.SSLError as e:
            raise RequestError(f"OG Pilot request failed with SSL error: {e}")
        except requests.exceptions.ConnectTimeout as e:
            raise RequestError(f"OG Pilot request timed out during connection: {e}")
        except requests.exceptions.ReadTimeout as e:
            raise RequestError(f"OG Pilot request timed out during read: {e}")
        except requests.exceptions.RequestException as e:
            raise RequestError(f"OG Pilot request failed: {e}")

    def _build_url(self, params: dict, iat: int | float | datetime | None) -> str:
        """Build the signed URL for the image request."""
        payload = self._build_payload(params, iat)
        token = jwt_encoder.encode(payload, self._api_key)
        base_url = urljoin(self.config.base_url, ENDPOINT_PATH)
        return f"{base_url}?{urlencode({'token': token})}"

    def _build_payload(self, params: dict, iat: int | float | datetime | None) -> dict:
        """Build the JWT payload with required claims."""
        payload = dict(params)

        if iat is not None:
            payload["iat"] = _normalize_iat(iat)

        if "iss" not in payload or not payload["iss"]:
            payload["iss"] = self._domain

        if "sub" not in payload or not payload["sub"]:
            payload["sub"] = self._api_key_prefix

        self._validate_payload(payload)
        return payload

    def _validate_payload(self, payload: dict) -> None:
        """Validate required payload fields."""
        if not payload.get("iss"):
            raise ConfigurationError("OG Pilot domain is missing")

        if not payload.get("sub"):
            raise ConfigurationError("OG Pilot API key prefix is missing")

        if not payload.get("title"):
            raise ValueError("OG Pilot title is required")

    @property
    def _api_key(self) -> str:
        """Get the API key, raising an error if not configured."""
        if self.config.api_key:
            return self.config.api_key
        raise ConfigurationError("OG Pilot API key is missing")

    @property
    def _domain(self) -> str:
        """Get the domain, raising an error if not configured."""
        if self.config.domain:
            return self.config.domain
        raise ConfigurationError("OG Pilot domain is missing")

    @property
    def _api_key_prefix(self) -> str:
        """Get the first 8 characters of the API key."""
        return self._api_key[:8]


def _normalize_iat(iat: int | float | datetime) -> int:
    """
    Normalize the iat (issued at) value to Unix timestamp seconds.

    Handles:
    - datetime objects
    - Unix timestamps in milliseconds (> 100000000000)
    - Unix timestamps in seconds
    """
    if isinstance(iat, datetime):
        return int(iat.timestamp())

    # If it looks like milliseconds, convert to seconds
    if iat > 100_000_000_000:
        return int(iat / 1000)

    return int(iat)
