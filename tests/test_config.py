"""Tests for og_pilot.config module."""

import os
from unittest.mock import patch

import pytest

from og_pilot.config import Configuration, DEFAULT_BASE_URL


class TestConfiguration:
    """Tests for the Configuration class."""

    def test_default_values(self):
        """Test that defaults are set correctly."""
        with patch.dict(os.environ, {}, clear=True):
            config = Configuration()
            assert config.api_key is None
            assert config.domain is None
            assert config.base_url == DEFAULT_BASE_URL
            assert config.open_timeout == 5.0
            assert config.read_timeout == 10.0

    def test_reads_from_env_vars(self):
        """Test that config reads from environment variables."""
        with patch.dict(
            os.environ,
            {
                "OG_PILOT_API_KEY": "test-api-key",
                "OG_PILOT_DOMAIN": "test.example.com",
            },
        ):
            config = Configuration()
            assert config.api_key == "test-api-key"
            assert config.domain == "test.example.com"

    def test_explicit_values_override_env(self):
        """Test that explicit values override environment variables."""
        with patch.dict(
            os.environ,
            {
                "OG_PILOT_API_KEY": "env-key",
                "OG_PILOT_DOMAIN": "env.example.com",
            },
        ):
            config = Configuration(
                api_key="explicit-key",
                domain="explicit.example.com",
            )
            assert config.api_key == "explicit-key"
            assert config.domain == "explicit.example.com"

    def test_custom_timeouts(self):
        """Test custom timeout values."""
        config = Configuration(
            open_timeout=15.0,
            read_timeout=30.0,
        )
        assert config.open_timeout == 15.0
        assert config.read_timeout == 30.0

    def test_custom_base_url(self):
        """Test custom base URL."""
        config = Configuration(base_url="https://custom.ogpilot.com")
        assert config.base_url == "https://custom.ogpilot.com"
