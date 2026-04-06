"""
OG Pilot Client

HTTP client for the OG Pilot API.
"""

from __future__ import annotations

import json as json_module
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import urlencode, urljoin, urlparse

import requests

from og_pilot import jwt_encoder
from og_pilot.exceptions import ConfigurationError, RequestError
from og_pilot.request_context import get_current_path

if TYPE_CHECKING:
    from og_pilot.config import Configuration


ENDPOINT_PATH = "/api/v1/images"
logger = logging.getLogger(__name__)


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
        params: dict[str, Any] | None = None,
        *,
        json_response: bool = False,
        iat: int | float | datetime | None = None,
        headers: dict[str, str] | None = None,
        default: bool = False,
    ) -> str | dict[str, Any] | None:
        """
        Generate an OG Pilot image URL or fetch JSON metadata.

        Args:
            params: Dictionary of template parameters (must include 'title')
            json_response: If True, return JSON metadata instead of URL
            iat: Issue time for cache busting. Can be Unix timestamp (int/float)
                 or datetime object. If omitted, image is cached indefinitely.
            headers: Additional HTTP headers to send with the request
            default: If True, force path to "/" regardless of current request

        Returns:
            Image URL string (final URL after redirects), JSON metadata dict if
            json_response=True, or a fail-safe fallback when generation fails:
            None for URL mode, {"image_url": None} for JSON mode.
        """
        try:
            # Always include a path; manual overrides win, otherwise resolve from current request
            resolved_params = self._apply_configured_image_defaults(dict(params or {}))
            manual_path = resolved_params.pop("path", None)
            resolved_params["path"] = self._resolve_path(manual_path, default)

            url = self._build_url(resolved_params, iat)
            response = self._request(url, json_response=json_response, headers=headers or {})

            if json_response:
                return cast(dict[str, Any], json_module.loads(response.text))

            # Return the final URL after redirects (with fallbacks for unusual responses)
            image_url = response.url or response.headers.get("Location") or str(url)
            return None if self._is_status_placeholder(image_url) else image_url
        except Exception as e:
            logger.error("OG Pilot create_image failed: %s", e, exc_info=True)
            if json_response:
                return {"image_url": None}
            return None

    def _apply_configured_image_defaults(self, params: dict[str, Any]) -> dict[str, Any]:
        """Fill in delivery options from client configuration when omitted."""
        defaults = {
            "image_type": self.config.image_type,
            "quality": self.config.quality,
            "max_bytes": self.config.max_bytes,
        }

        for key, value in defaults.items():
            if value is not None and key not in params:
                params[key] = value

        return params

    def _resolve_path(self, manual_path: Any, use_default: bool) -> str:
        """
        Resolve the path parameter for the request.

        Priority: manual path > current request path > "/"
        """
        # Manual path always wins if provided
        if manual_path is not None:
            path_str = str(manual_path).strip()
            if path_str:
                return self._normalize_path(path_str)

        # If default is true, return "/"
        if use_default:
            return "/"

        # Try to get path from current request context
        current_path = get_current_path()
        return self._normalize_path(current_path)

    def _normalize_path(self, path: str | None) -> str:
        """
        Normalize a path to ensure it starts with "/" and handles full URLs.
        """
        if path is None or path == "":
            return "/"

        cleaned = path.strip()
        if not cleaned:
            return "/"

        # Extract path from full URLs
        if cleaned.startswith(("http://", "https://")):
            parsed = urlparse(cleaned)
            url_path = parsed.path or "/"
            query = parsed.query
            cleaned = f"{url_path}?{query}" if query else url_path

        # Ensure path starts with "/"
        if not cleaned.startswith("/"):
            cleaned = "/" + cleaned

        if self.config.strip_extensions:
            cleaned = self._strip_extension(cleaned)

        if self.config.strip_query_parameters:
            cleaned = self._drop_query_parameters(cleaned)

        return cleaned

    def _strip_extension(self, path: str) -> str:
        """
        Strip file extensions from the last path segment.

        Removes all extensions (e.g., /archive.tar.gz -> /archive).
        Dotfiles like /.hidden are left unchanged.
        """
        question_idx = path.find("?")
        if question_idx >= 0:
            path_part = path[:question_idx]
            query = path[question_idx + 1:]
        else:
            path_part = path
            query = None

        last_slash = path_part.rfind("/")
        if last_slash >= 0:
            dir_part = path_part[:last_slash]
            base = path_part[last_slash + 1:]
        else:
            dir_part = ""
            base = path_part

        # Don't strip dotfiles like ".hidden" or ".env"
        if base.startswith("."):
            return path

        dot_idx = base.find(".")
        if dot_idx < 0:
            return path  # no extension to strip

        stripped = base[:dot_idx]
        result = f"{dir_part}/{stripped}" if dir_part else f"/{stripped}"
        if not result:
            result = "/"

        return f"{result}?{query}" if query is not None else result

    def _drop_query_parameters(self, path: str) -> str:
        """
        Remove the query string from the resolved path if present.
        """
        question_idx = path.find("?")
        return path[:question_idx] if question_idx >= 0 else path

    @staticmethod
    def _is_status_placeholder(url: str) -> bool:
        """Check if URL is a status placeholder (processing/failed)."""
        import re
        return bool(re.search(r"/status/(?:processing|failed)\.(?:jpg|png)$", url))

    def _request(
        self,
        url: str,
        *,
        json_response: bool,
        headers: dict[str, str],
    ) -> requests.Response:
        """Make an HTTP POST request to the OG Pilot API."""
        request_headers = {}
        if json_response:
            request_headers["Accept"] = "application/json"
        request_headers.update(headers)

        timeout = (self.config.open_timeout, self.config.read_timeout)

        try:
            response = requests.post(
                url,
                headers=request_headers,
                timeout=timeout,
                allow_redirects=True,
            )

            if response.status_code >= 400:
                raise RequestError(
                    f"OG Pilot request failed with status {response.status_code}: {response.text}",
                    status_code=response.status_code,
                )

            return response

        except requests.exceptions.SSLError as e:
            raise RequestError(f"OG Pilot request failed with SSL error: {e}") from e
        except requests.exceptions.ConnectTimeout as e:
            raise RequestError(f"OG Pilot request timed out during connection: {e}") from e
        except requests.exceptions.ReadTimeout as e:
            raise RequestError(f"OG Pilot request timed out during read: {e}") from e
        except requests.exceptions.RequestException as e:
            raise RequestError(f"OG Pilot request failed: {e}") from e

    def _build_url(self, params: dict[str, Any], iat: int | float | datetime | None) -> str:
        """Build the signed URL for the image request."""
        payload = self._build_payload(params, iat)
        token = jwt_encoder.encode(payload, self._api_key)
        base_url = urljoin(self.config.base_url, ENDPOINT_PATH)
        return f"{base_url}?{urlencode({'token': token})}"

    def _build_payload(self, params: dict[str, Any], iat: int | float | datetime | None) -> dict[str, Any]:
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

    def _validate_payload(self, payload: dict[str, Any]) -> None:
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
