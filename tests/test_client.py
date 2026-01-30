"""Tests for og_pilot.client module."""

from datetime import datetime

import pytest
import responses

from og_pilot.client import Client, _normalize_iat
from og_pilot.config import Configuration
from og_pilot.exceptions import ConfigurationError, RequestError


class TestNormalizeIat:
    """Tests for the _normalize_iat helper function."""

    def test_datetime_object(self):
        """Test normalizing a datetime object."""
        dt = datetime(2024, 1, 15, 12, 0, 0)
        result = _normalize_iat(dt)
        assert result == int(dt.timestamp())

    def test_unix_seconds(self):
        """Test normalizing Unix timestamp in seconds."""
        timestamp = 1705320000  # 2024-01-15 12:00:00 UTC
        result = _normalize_iat(timestamp)
        assert result == timestamp

    def test_unix_milliseconds(self):
        """Test normalizing Unix timestamp in milliseconds."""
        timestamp_ms = 1705320000000
        result = _normalize_iat(timestamp_ms)
        assert result == 1705320000

    def test_float_seconds(self):
        """Test normalizing float timestamp."""
        timestamp = 1705320000.5
        result = _normalize_iat(timestamp)
        assert result == 1705320000


class TestClient:
    """Tests for the Client class."""

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

    def test_init(self, config):
        """Test client initialization."""
        client = Client(config)
        assert client.config == config

    def test_api_key_missing_raises_error(self):
        """Test that missing API key raises ConfigurationError."""
        config = Configuration(domain="test.com")
        client = Client(config)

        with pytest.raises(ConfigurationError, match="API key is missing"):
            client.create_image({"title": "Test"})

    def test_domain_missing_raises_error(self):
        """Test that missing domain raises ConfigurationError."""
        config = Configuration(api_key="test-key-12345678")
        client = Client(config)

        with pytest.raises(ConfigurationError, match="domain is missing"):
            client.create_image({"title": "Test"})

    def test_title_required(self, client):
        """Test that title is required."""
        with pytest.raises(ValueError, match="title is required"):
            client.create_image({"template": "default"})

    def test_api_key_prefix(self, client):
        """Test that API key prefix is first 8 characters."""
        assert client._api_key_prefix == "test-api"

    @responses.activate
    def test_create_image_returns_url(self, client):
        """Test that create_image returns the redirect location."""
        responses.add(
            responses.GET,
            "https://ogpilot.com/api/v1/images",
            status=302,
            headers={"Location": "https://cdn.ogpilot.com/image.png"},
        )

        url = client.create_image({"title": "Test Title", "template": "default"})
        assert url == "https://cdn.ogpilot.com/image.png"

    @responses.activate
    def test_create_image_json_response(self, client):
        """Test that create_image returns JSON when requested."""
        responses.add(
            responses.GET,
            "https://ogpilot.com/api/v1/images",
            json={"url": "https://cdn.ogpilot.com/image.png", "width": 1200},
            status=200,
        )

        result = client.create_image(
            {"title": "Test Title", "template": "default"},
            json_response=True,
        )
        assert result["url"] == "https://cdn.ogpilot.com/image.png"
        assert result["width"] == 1200

    @responses.activate
    def test_request_error_on_4xx(self, client):
        """Test that 4xx responses raise RequestError."""
        responses.add(
            responses.GET,
            "https://ogpilot.com/api/v1/images",
            status=400,
            body="Bad request",
        )

        with pytest.raises(RequestError, match="status 400"):
            client.create_image({"title": "Test"})

    @responses.activate
    def test_request_error_on_5xx(self, client):
        """Test that 5xx responses raise RequestError."""
        responses.add(
            responses.GET,
            "https://ogpilot.com/api/v1/images",
            status=500,
            body="Internal server error",
        )

        with pytest.raises(RequestError, match="status 500"):
            client.create_image({"title": "Test"})
