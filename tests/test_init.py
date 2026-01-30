"""Tests for og_pilot module-level functions."""

import os
from unittest.mock import patch

import pytest

import og_pilot
from og_pilot import Client, Configuration


class TestModuleFunctions:
    """Tests for module-level convenience functions."""

    def setup_method(self):
        """Reset config before each test."""
        og_pilot.reset_config()

    def teardown_method(self):
        """Reset config after each test."""
        og_pilot.reset_config()

    def test_get_config_creates_default(self):
        """Test that get_config creates a default configuration."""
        config = og_pilot.get_config()
        assert isinstance(config, Configuration)

    def test_get_config_returns_same_instance(self):
        """Test that get_config returns the same instance."""
        config1 = og_pilot.get_config()
        config2 = og_pilot.get_config()
        assert config1 is config2

    def test_configure_updates_config(self):
        """Test that configure updates the global configuration."""
        og_pilot.configure(
            api_key="test-key",
            domain="test.com",
        )
        config = og_pilot.get_config()
        assert config.api_key == "test-key"
        assert config.domain == "test.com"

    def test_configure_partial_update(self):
        """Test that configure can do partial updates."""
        og_pilot.configure(api_key="first-key")
        og_pilot.configure(domain="test.com")

        config = og_pilot.get_config()
        assert config.api_key == "first-key"
        assert config.domain == "test.com"

    def test_reset_config(self):
        """Test that reset_config clears the configuration."""
        og_pilot.configure(api_key="test-key")
        og_pilot.reset_config()

        with patch.dict(os.environ, {}, clear=True):
            og_pilot.reset_config()  # Reset again to clear cached config
            config = og_pilot.get_config()
            assert config.api_key is None

    def test_client_returns_client_instance(self):
        """Test that client() returns a Client instance."""
        client = og_pilot.client()
        assert isinstance(client, Client)

    def test_create_client_with_options(self):
        """Test that create_client creates client with custom options."""
        client = og_pilot.create_client(
            api_key="custom-key",
            domain="custom.com",
        )
        assert isinstance(client, Client)
        assert client.config.api_key == "custom-key"
        assert client.config.domain == "custom.com"

    def test_exports(self):
        """Test that all expected names are exported."""
        expected_exports = [
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
        for name in expected_exports:
            assert hasattr(og_pilot, name), f"Missing export: {name}"
