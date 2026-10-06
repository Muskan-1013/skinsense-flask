"""Central configuration for SkinSense."""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # Set SECRET_KEY and DATABASE_URL in the environment on your host.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-key")
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    MIN_PASSWORD_LENGTH = 8
    # Stay signed in for 30 days so returning users go straight to the home page
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 30
    MAX_MESSAGE_LENGTH = 2000


class TestConfig(Config):
    TESTING = True