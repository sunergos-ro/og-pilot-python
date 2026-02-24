"""Tests for og_pilot.client module."""

import logging
from datetime import datetime
from urllib.parse import parse_qs, urlparse

import jwt
import pytest
import responses

from og_pilot.client import Client, _normalize_iat
from og_pilot.config import Configuration


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

    def test_api_key_missing_returns_none_and_logs_error(self, caplog):
        """Test that missing API key returns None and logs an error."""
        config = Configuration(domain="test.com")
        client = Client(config)

        with caplog.at_level(logging.ERROR, logger="og_pilot.client"):
            result = client.create_image({"title": "Test"})

        assert result is None
        assert "OG Pilot create_image failed" in caplog.text
        assert "API key is missing" in caplog.text

    def test_domain_missing_returns_none_and_logs_error(self, caplog):
        """Test that missing domain returns None and logs an error."""
        config = Configuration(api_key="test-key-12345678")
        client = Client(config)

        with caplog.at_level(logging.ERROR, logger="og_pilot.client"):
            result = client.create_image({"title": "Test"})

        assert result is None
        assert "OG Pilot create_image failed" in caplog.text
        assert "domain is missing" in caplog.text

    def test_title_missing_returns_none_and_logs_error(self, client, caplog):
        """Test that missing title returns None and logs an error."""
        with caplog.at_level(logging.ERROR, logger="og_pilot.client"):
            result = client.create_image({"template": "default"})

        assert result is None
        assert "OG Pilot create_image failed" in caplog.text
        assert "title is required" in caplog.text

    def test_api_key_prefix(self, client):
        """Test that API key prefix is first 8 characters."""
        assert client._api_key_prefix == "test-api"

    @responses.activate
    def test_create_image_returns_url(self, client):
        """Test that create_image follows redirects and returns the final URL."""
        responses.add(
            responses.POST,
            "https://ogpilot.com/api/v1/images",
            status=302,
            headers={"Location": "https://cdn.ogpilot.com/image.png"},
        )
        responses.add(
            responses.GET,
            "https://cdn.ogpilot.com/image.png",
            status=200,
            body="mock-image-bytes",
            content_type="image/png",
        )

        url = client.create_image({"title": "Test Title", "template": "default"})
        assert url == "https://cdn.ogpilot.com/image.png"
        assert len(responses.calls) == 2

        first_request = responses.calls[0].request
        assert first_request.method == "POST"

        parsed = urlparse(first_request.url)
        assert parsed.path == "/api/v1/images"
        token = parse_qs(parsed.query)["token"][0]
        payload = jwt.decode(token, client.config.api_key, algorithms=["HS256"])
        assert payload["title"] == "Test Title"
        assert payload["template"] == "default"

        second_request = responses.calls[1].request
        assert second_request.method == "GET"
        assert second_request.url == "https://cdn.ogpilot.com/image.png"

    @responses.activate
    def test_create_image_json_response(self, client):
        """Test that create_image returns JSON when requested."""
        responses.add(
            responses.POST,
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

        request = responses.calls[0].request
        assert request.method == "POST"
        assert request.headers["Accept"] == "application/json"

    @responses.activate
    def test_request_error_on_4xx_returns_none_and_logs(self, client, caplog):
        """Test that 4xx responses do not raise and return None."""
        responses.add(
            responses.POST,
            "https://ogpilot.com/api/v1/images",
            status=400,
            body="Bad request",
        )

        with caplog.at_level(logging.ERROR, logger="og_pilot.client"):
            result = client.create_image({"title": "Test"})

        assert result is None
        assert "OG Pilot create_image failed" in caplog.text
        assert "status 400" in caplog.text

    @responses.activate
    def test_request_error_on_5xx_json_response_returns_fallback_and_logs(self, client, caplog):
        """Test that 5xx responses with json_response return fallback data."""
        responses.add(
            responses.POST,
            "https://ogpilot.com/api/v1/images",
            status=500,
            body="Internal server error",
        )

        with caplog.at_level(logging.ERROR, logger="og_pilot.client"):
            result = client.create_image({"title": "Test"}, json_response=True)

        assert result == {"image_url": None}
        assert "OG Pilot create_image failed" in caplog.text
        assert "status 500" in caplog.text
