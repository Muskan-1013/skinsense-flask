"""Central configuration for SkinSense."""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # Set SECRET_KEY in the environment on your host. The fallback is for local use only.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-key")
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    MIN_PASSWORD_LENGTH = 8
    # Stay signed in for 30 days so returning users go straight to the home page
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 30
    MAX_MESSAGE_LENGTH = 2000
    # Old plain-text files that are imported once, then renamed to *.migrated



class TestConfig(Config):
    TESTING = True
    DATABASE_PATH = ":memory:"