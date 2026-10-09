"""Central configuration for SkinSense."""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # Set SECRET_KEY and DATABASE_URL in the environment on your host.
    # No default: create_app() must refuse to start without a real key.
    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    MIN_PASSWORD_LENGTH = 8
    # Stay signed in for 30 days so returning users go straight to the home page
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 30
    MAX_MESSAGE_LENGTH = 2000

    SESSION_COOKIE_SECURE = True      # set False only for local http testing
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-only-key"
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False