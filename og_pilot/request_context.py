"""
OG Pilot Request Context

Provides request context management for automatic path resolution.
Uses contextvars for async-safe storage of the current request.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from contextvars import ContextVar
from typing import TypeVar
from urllib.parse import urlparse

# Context variable for storing the current request info
_current_request: ContextVar[dict[str, str] | None] = ContextVar("og_pilot_request", default=None)

T = TypeVar("T")


def set_current_request(request: dict[str, str]) -> None:
    """
    Set the current request context for automatic path resolution.

    Call this in your middleware/request handler before using OG Pilot.

    Args:
        request: Dictionary with 'url' and/or 'path' keys

    Example (Django middleware):
        >>> class OgPilotMiddleware:
        ...     def __init__(self, get_response):
        ...         self.get_response = get_response
        ...
        ...     def __call__(self, request):
        ...         set_current_request({'url': request.get_full_path()})
        ...         try:
        ...             return self.get_response(request)
        ...         finally:
        ...             clear_current_request()

    Example (Flask):
        >>> @app.before_request
        ... def set_og_pilot_context():
        ...     set_current_request({'url': request.full_path})
        ...
        >>> @app.after_request
        ... def clear_og_pilot_context(response):
        ...     clear_current_request()
        ...     return response

    Example (FastAPI):
        >>> @app.middleware("http")
        ... async def og_pilot_middleware(request: Request, call_next):
        ...     set_current_request({'url': str(request.url.path)})
        ...     try:
        ...         return await call_next(request)
        ...     finally:
        ...         clear_current_request()
    """
    _current_request.set(request)


def clear_current_request() -> None:
    """
    Clear the current request context.

    Call this after the request is complete.
    """
    _current_request.set(None)


def get_current_request() -> dict[str, str] | None:
    """
    Get the current request info.

    Returns:
        Dictionary with request info, or None if not set
    """
    return _current_request.get()


def with_request_context(request: dict[str, str], callback: Callable[[], T]) -> T:
    """
    Run a callback with the given request context.

    The context is automatically restored after the callback completes,
    even if an exception is raised.

    Args:
        request: Dictionary with 'url' and/or 'path' keys
        callback: Function to execute with the request context

    Returns:
        The result of the callback

    Example:
        >>> def generate_og_image():
        ...     return og_pilot.create_image(title="Hello")
        ...
        >>> url = with_request_context(
        ...     {'url': '/blog/my-post'},
        ...     generate_og_image
        ... )
    """
    token = _current_request.set(request)
    try:
        return callback()
    finally:
        _current_request.reset(token)


def get_current_path() -> str | None:
    """
    Get the current request path from context, framework, or environment.

    Checks (in order):
    1. Explicit 'path' key in request context (set via set_current_request)
    2. Path extracted from 'url' key in request context
    3. Auto-detected from web framework (Flask, Django)
    4. Environment variables (REQUEST_URI, ORIGINAL_FULLPATH, PATH_INFO, REQUEST_PATH)

    Returns:
        The current path, or None if not available
    """
    request = get_current_request()

    # Check explicit path first
    if request and request.get("path"):
        return request["path"]

    # Extract path from URL
    if request and request.get("url"):
        return _extract_path_from_url(request["url"])

    # Try to auto-detect from web framework
    framework_path = _get_path_from_framework()
    if framework_path:
        return framework_path

    # Fallback to environment variables
    return _get_path_from_env()


def _extract_path_from_url(url: str) -> str:
    """Extract the path (with query string) from a URL."""
    # Handle full URLs
    if url.startswith(("http://", "https://")):
        parsed = urlparse(url)
        path = parsed.path or "/"
        query = parsed.query
        return f"{path}?{query}" if query else path

    return url


def _get_path_from_framework() -> str | None:
    """
    Auto-detect the current request path from common web frameworks.

    Supports:
    - Flask: Uses flask.request automatically (no setup needed)
    - Django: Uses thread-local request if available (requires middleware like
              django-crequest, or our OgPilotMiddleware)
    """
    # Try Flask first (most common, works out of the box)
    try:
        from flask import has_request_context
        from flask import request as flask_request

        if has_request_context():
            # full_path includes query string but may have trailing '?'
            path: str = flask_request.full_path
            return path.rstrip("?") if path.endswith("?") else path
    except ImportError:
        pass
    except RuntimeError:
        # Flask raises RuntimeError if accessed outside request context
        pass

    # Try Django thread-local request (works with django-crequest or similar)
    try:
        # Check if django-crequest is installed and has a request
        from crequest.middleware import CrequestMiddleware

        request = CrequestMiddleware.get_request()
        if request is not None:
            result: str = request.get_full_path()
            return result
    except ImportError:
        pass
    except Exception:
        pass

    # Note: FastAPI/Starlette don't have a global request context.
    # Users need to use set_current_request() in middleware for those frameworks.

    return None


def _get_path_from_env() -> str | None:
    """Get the path from environment variables."""
    # Check various environment variables (similar to Ruby implementation)
    request_uri = os.environ.get("REQUEST_URI")
    if request_uri:
        return request_uri

    original_fullpath = os.environ.get("ORIGINAL_FULLPATH")
    if original_fullpath:
        return original_fullpath

    path_info = os.environ.get("PATH_INFO")
    if path_info:
        query_string = os.environ.get("QUERY_STRING", "")
        return f"{path_info}?{query_string}" if query_string else path_info

    request_path = os.environ.get("REQUEST_PATH")
    if request_path:
        return request_path

    return None
