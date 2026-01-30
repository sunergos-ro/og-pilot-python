"""
OG Pilot Configuration Check Command

Management command to verify OG Pilot configuration.
"""

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand

import og_pilot
from og_pilot.exceptions import ConfigurationError


class Command(BaseCommand):
    """Check OG Pilot configuration and test connectivity."""

    help = "Check OG Pilot configuration and optionally test with a sample request"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--test",
            action="store_true",
            help="Send a test request to verify API connectivity",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Checking OG Pilot configuration...\n")

        config = og_pilot.get_config()

        # Check API key
        if config.api_key:
            masked_key = config.api_key[:4] + "*" * (len(config.api_key) - 8) + config.api_key[-4:]
            self.stdout.write(self.style.SUCCESS(f"  API Key: {masked_key}"))
        else:
            self.stdout.write(self.style.ERROR("  API Key: NOT SET"))
            self.stdout.write(
                "    Set OG_PILOT_API_KEY env var or OG_PILOT['API_KEY'] in settings"
            )

        # Check domain
        if config.domain:
            self.stdout.write(self.style.SUCCESS(f"  Domain: {config.domain}"))
        else:
            self.stdout.write(self.style.ERROR("  Domain: NOT SET"))
            self.stdout.write(
                "    Set OG_PILOT_DOMAIN env var or OG_PILOT['DOMAIN'] in settings"
            )

        # Show other settings
        self.stdout.write(f"  Base URL: {config.base_url}")
        self.stdout.write(f"  Open Timeout: {config.open_timeout}s")
        self.stdout.write(f"  Read Timeout: {config.read_timeout}s")

        if options["test"]:
            self.stdout.write("\nTesting API connectivity...")
            try:
                url = og_pilot.create_image(
                    template="default",
                    title="OG Pilot Test Image",
                )
                self.stdout.write(self.style.SUCCESS("  Success! Generated URL:"))
                self.stdout.write(f"  {url}")
            except ConfigurationError as e:
                self.stdout.write(self.style.ERROR(f"  Configuration Error: {e}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error: {e}"))
