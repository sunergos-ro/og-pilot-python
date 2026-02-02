"""Minimal Django settings for mypy/django-stubs."""

SECRET_KEY = "test-secret-key-for-mypy"
DEBUG = True
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "og_pilot.django",
]
USE_TZ = True
