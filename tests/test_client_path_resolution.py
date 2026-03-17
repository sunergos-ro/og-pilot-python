"""Tests for path resolution in og_pilot.client module."""

import pytest

from og_pilot.client import Client
from og_pilot.config import Configuration
from og_pilot.request_context import clear_current_request, set_current_request


class TestResolvePath:
    """Tests for the Client._resolve_path method."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return Configuration(
            api_key="test-api-key-12345678",
            domain="test.example.com",
        )

    @pytest.fixture
    def client(self, config):
        """Create a test client."""
        return Client(config)

    def setup_method(self):
        """Clear request context before each test."""
        clear_current_request()

    def teardown_method(self):
        """Clear request context after each test."""
        clear_current_request()

    def test_manual_path_wins(self, client):
        """Test that manual path takes priority."""
        set_current_request({"url": "/context/path"})
        path = client._resolve_path("/manual/path", False)
        assert path == "/manual/path"

    def test_manual_path_normalized(self, client):
        """Test that manual path is normalized."""
        path = client._resolve_path("manual/path", False)
        assert path == "/manual/path"

    def test_default_returns_slash(self, client):
        """Test that default=True returns '/'."""
        set_current_request({"url": "/should/be/ignored"})
        path = client._resolve_path(None, True)
        assert path == "/"

    def test_manual_wins_over_default(self, client):
        """Test that manual path wins over default=True."""
        path = client._resolve_path("/manual", True)
        assert path == "/manual"

    def test_uses_request_context(self, client):
        """Test that request context is used when no manual path."""
        set_current_request({"url": "/context/path?query=1"})
        path = client._resolve_path(None, False)
        assert path == "/context/path?query=1"

    def test_returns_slash_when_no_path(self, client):
        """Test that '/' is returned when no path is available."""
        clear_current_request()
        path = client._resolve_path(None, False)
        assert path == "/"

    def test_empty_manual_path_uses_context(self, client):
        """Test that empty manual path falls through to context."""
        set_current_request({"url": "/context"})
        path = client._resolve_path("", False)
        assert path == "/context"

    def test_whitespace_manual_path_uses_context(self, client):
        """Test that whitespace-only manual path falls through to context."""
        set_current_request({"url": "/context"})
        path = client._resolve_path("   ", False)
        assert path == "/context"


class TestNormalizePath:
    """Tests for the Client._normalize_path method."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return Configuration(
            api_key="test-api-key-12345678",
            domain="test.example.com",
        )

    @pytest.fixture
    def client(self, config):
        """Create a test client."""
        return Client(config)

    def test_none_returns_slash(self, client):
        """Test that None returns '/'."""
        path = client._normalize_path(None)
        assert path == "/"

    def test_empty_string_returns_slash(self, client):
        """Test that empty string returns '/'."""
        path = client._normalize_path("")
        assert path == "/"

    def test_whitespace_returns_slash(self, client):
        """Test that whitespace-only returns '/'."""
        path = client._normalize_path("   ")
        assert path == "/"

    def test_adds_leading_slash(self, client):
        """Test that leading slash is added."""
        path = client._normalize_path("foo/bar")
        assert path == "/foo/bar"

    def test_keeps_existing_slash(self, client):
        """Test that existing leading slash is preserved."""
        path = client._normalize_path("/foo/bar")
        assert path == "/foo/bar"

    def test_extracts_from_full_url(self, client):
        """Test that path is extracted from full URL."""
        path = client._normalize_path("https://example.com/foo/bar?query=1")
        assert path == "/foo/bar?query=1"

    def test_extracts_from_http_url(self, client):
        """Test that path is extracted from HTTP URL."""
        path = client._normalize_path("http://example.com/path")
        assert path == "/path"

    def test_full_url_without_path(self, client):
        """Test URL without path."""
        path = client._normalize_path("https://example.com")
        assert path == "/"

    def test_trims_whitespace(self, client):
        """Test that whitespace is trimmed."""
        path = client._normalize_path("  /foo/bar  ")
        assert path == "/foo/bar"

    def test_preserves_query_string(self, client):
        """Test that query string is preserved."""
        path = client._normalize_path("/foo?bar=baz&qux=1")
        assert path == "/foo?bar=baz&qux=1"

    def test_strip_query_parameters_removes_query_when_enabled(self, client):
        """Test that query string is dropped when strip_query_parameters is True."""
        client.config.strip_query_parameters = True
        path = client._normalize_path("/foo?bar=baz&qux=1")
        assert path == "/foo"
