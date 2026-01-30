"""
OG Pilot Django App Configuration
"""

from django.apps import AppConfig
from django.conf import settings


class OgPilotConfig(AppConfig):
    """Django app configuration for OG Pilot."""

    name = "og_pilot.django"
    verbose_name = "OG Pilot"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        """Configure OG Pilot from Django settings when the app is ready."""
        import og_pilot

        # Get OG_PILOT settings dict, defaulting to empty dict
        og_pilot_settings = getattr(settings, "OG_PILOT", {})

        config_mapping = {
            "API_KEY": "api_key",
            "DOMAIN": "domain",
            "BASE_URL": "base_url",
            "OPEN_TIMEOUT": "open_timeout",
            "READ_TIMEOUT": "read_timeout",
        }

        config_kwargs = {}
        for settings_key, config_key in config_mapping.items():
            if settings_key in og_pilot_settings:
                config_kwargs[config_key] = og_pilot_settings[settings_key]

        if config_kwargs:
            og_pilot.configure(**config_kwargs)
