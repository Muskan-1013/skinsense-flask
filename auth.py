"""Password hashing, input validation and the login_required decorator."""

import re
from functools import wraps

from flask import redirect, session
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(email):
    return (email or "").strip().lower()


def is_valid_email(email):
    return bool(EMAIL_PATTERN.match(email)) and len(email) <= 254


def password_error(password):
    """Return a message if the password is unacceptable, else None."""
    if len(password) < Config.MIN_PASSWORD_LENGTH:
        return "Password must be at least %d characters." % Config.MIN_PASSWORD_LENGTH
    if password.isdigit() or password.isalpha():
        return "Use a mix of letters and numbers."
    return None


def hash_password(password):
    return generate_password_hash(password)


def verify_password(stored_hash, password):
    return check_password_hash(stored_hash, password)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return view(*args, **kwargs)
    return wrapped