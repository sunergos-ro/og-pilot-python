"""
OG Pilot Django Integration

Django app for easy OG Pilot integration.

Add 'og_pilot.django' to your INSTALLED_APPS to use template tags and
management commands.

Example settings.py:
    INSTALLED_APPS = [
        ...
        'og_pilot.django',
    ]

    OG_PILOT = {
        'API_KEY': 'your-api-key',  # or use OG_PILOT_API_KEY env var
        'DOMAIN': 'example.com',     # or use OG_PILOT_DOMAIN env var
    }
"""

default_app_config = "og_pilot.django.apps.OgPilotConfig"
