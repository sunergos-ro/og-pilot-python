"""Tests for og_pilot module-level functions."""

import os
from unittest.mock import patch

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
            image_type="webp",
            quality=82,
            max_bytes=220000,
        )
        config = og_pilot.get_config()
        assert config.api_key == "test-key"
        assert config.domain == "test.com"
        assert config.image_type == "webp"
        assert config.quality == 82
        assert config.max_bytes == 220000

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
            "create_blog_post_image",
            "create_podcast_image",
            "create_product_image",
            "create_event_image",
            "create_book_image",
            "create_company_image",
            "create_portfolio_image",
        ]
        for name in expected_exports:
            assert hasattr(og_pilot, name), f"Missing export: {name}"

    def test_template_helpers_force_expected_template(self):
        """Test that template helpers always send their template."""

        class StubClient:
            def __init__(self):
                self.calls = []

            def create_image(
                self,
                params,
                *,
                json_response=False,
                iat=None,
                headers=None,
                default=False,
            ):
                self.calls.append(
                    {
                        "params": params,
                        "json_response": json_response,
                        "iat": iat,
                        "headers": headers,
                        "default": default,
                    }
                )
                return "ok"

        stub_client = StubClient()
        helpers = {
            "create_blog_post_image": "blog_post",
            "create_podcast_image": "podcast",
            "create_product_image": "product",
            "create_event_image": "event",
            "create_book_image": "book",
            "create_company_image": "company",
            "create_portfolio_image": "portfolio",
        }

        with patch("og_pilot.client", return_value=stub_client):
            for helper_name, expected_template in helpers.items():
                helper = getattr(og_pilot, helper_name)
                result = helper(
                    {"title": "Hello", "template": "page"},
                    json_response=True,
                    iat=123,
                    headers={"X-Test": "1"},
                    default=True,
                    template="ignored",
                )

                assert result == "ok"
                call = stub_client.calls[-1]
                assert call["params"]["title"] == "Hello"
                assert call["params"]["template"] == expected_template
                assert call["json_response"] is True
                assert call["iat"] == 123
                assert call["headers"] == {"X-Test": "1"}
                assert call["default"] is True
