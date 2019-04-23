"""
Django settings for tests.

Inspired from: https://github.com/jazzband/django-debug-toolbar/blob/master/tests/settings.py
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production

SECRET_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

LOGGING_CONFIG = None  # avoids spurious output in tests


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "djhubspot",
]

ROOT_URLCONF = "tests.urls"

# Cache and database

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}


# DJHubspot settings
# ------------------------------------------------------------------------------

HUBSPOT_API_KEY = '__API_KEY__'
# FIXME: This is currently used to test the hubspot authentication. Unit test are passing with
# FIXME: the real app secret but it should not be pushed to the repo. Make it works with a random
# FIXME: APP_SECRET.
HUBSPOT_APP_SECRET = None
