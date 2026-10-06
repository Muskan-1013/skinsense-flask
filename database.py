"""Postgres storage: connection handling, versioned migrations and queries."""

import hashlib
import secrets

import psycopg2
import psycopg2.errors
import psycopg2.extras
from flask import current_app, g

MIGRATIONS = [
    """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE TABLE contacts (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE TABLE waitlist (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        skintype TEXT NOT NULL DEFAULT '',
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """,
    """
    CREATE TABLE devices (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token_hash TEXT NOT NULL UNIQUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        last_seen TIMESTAMPTZ
    );
    CREATE TABLE pairing (
        code TEXT PRIMARY KEY,
        expires_at TIMESTAMPTZ NOT NULL,
        user_id INTEGER,
        token TEXT
    );
    CREATE TABLE readings (
        id SERIAL PRIMARY KEY,
        device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        moisture REAL NOT NULL,
        ph REAL NOT NULL,
        oiliness REAL NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX readings_user_time ON readings (user_id, created_at);
    """,
]


# ---------- connection handling ----------

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(current_app.config["DATABASE_URL"])
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _run(sql, args=(), fetch=None):
    """Run one statement, commit, and roll back on any error."""
    db = get_db()
    try:
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, args)
            result = None
            if fetch == "one":
                result = cur.fetchone()
            elif fetch == "all":
                result = cur.fetchall()
            rowcount = cur.rowcount
        db.commit()
        return result if fetch else rowcount
    except Exception:
        db.rollback()
        raise


def run_migrations(db):
    with db.cursor() as cur:
        cur.execute("SELECT pg_advisory_lock(727274)")  # one gunicorn worker at a time
        cur.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)")
        cur.execute("SELECT version FROM schema_version")
        row = cur.fetchone()
        if row is None:
            cur.execute("INSERT INTO schema_version VALUES (0)")
        version = row[0] if row else 0
        for number in range(version, len(MIGRATIONS)):
            cur.execute(MIGRATIONS[number])
            cur.execute("UPDATE schema_version SET version = %s", (number + 1,))
        db.commit()
        cur.execute("SELECT pg_advisory_unlock(727274)")
    db.commit()


def init_db(app):
    """Create/upgrade the schema. Call once at startup."""
    if not app.config["DATABASE_URL"]:
        raise RuntimeError("DATABASE_URL is not set")
    app.teardown_appcontext(close_db)
    with app.app_context():
        run_migrations(get_db())


# ---------- users, contacts, waitlist ----------

def create_user(email, password_hash):
    """Returns the new id, or None if the email already exists."""
    try:
        row = _run(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
            (email, password_hash), fetch="one",
        )
        return row["id"]
    except psycopg2.errors.UniqueViolation:
        return None


def get_user_by_email(email):
    return _run("SELECT * FROM users WHERE email = %s", (email,), fetch="one")


def add_contact(name, email, message):
    _run("INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)", (name, email, message))


def add_waitlist(name, email, skintype):
    """Returns True if added, False if the email was already on the list."""
    try:
        _run("INSERT INTO waitlist (name, email, skintype) VALUES (%s, %s, %s)", (name, email, skintype))
        return True
    except psycopg2.errors.UniqueViolation:
        return False


# ---------- device pairing ----------

def create_pairing(code):
    """Device announces a code. False if that code is still live for someone else."""
    count = _run(
        """INSERT INTO pairing (code, expires_at) VALUES (%s, now() + interval '10 minutes')
           ON CONFLICT (code) DO UPDATE
             SET expires_at = EXCLUDED.expires_at, user_id = NULL, token = NULL
             WHERE pairing.expires_at < now()""",
        (code,),
    )
    return count == 1


def claim_pairing(code, user_id):
    """User typed the code on the website. Creates the device and a token for it."""
    token = secrets.token_urlsafe(32)
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                """UPDATE pairing SET user_id = %s, token = %s
                   WHERE code = %s AND user_id IS NULL AND expires_at > now()""",
                (user_id, token, code),
            )
            if cur.rowcount == 0:
                db.rollback()
                return False
            cur.execute(
                "INSERT INTO devices (user_id, token_hash) VALUES (%s, %s)",
                (user_id, hashlib.sha256(token.encode()).hexdigest()),
            )
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise


def collect_pairing(code):
    """Device picks up its token once. Returns the token or None."""
    row = _run(
        "DELETE FROM pairing WHERE code = %s AND token IS NOT NULL RETURNING token",
        (code,), fetch="one",
    )
    return row["token"] if row else None


# ---------- readings ----------

def get_device_by_token(token):
    return _run(
        """UPDATE devices SET last_seen = now() WHERE token_hash = %s
           RETURNING id, user_id""",
        (hashlib.sha256(token.encode()).hexdigest(),), fetch="one",
    )


def add_reading(device, moisture, ph, oiliness):
    _run(
        """INSERT INTO readings (device_id, user_id, moisture, ph, oiliness)
           VALUES (%s, %s, %s, %s, %s)""",
        (device["id"], device["user_id"], moisture, ph, oiliness),
    )


def get_readings(user_id, limit=300):
    """Newest first."""
    return _run(
        "SELECT * FROM readings WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
        (user_id, limit), fetch="all",
    )


def count_devices(user_id):
    return _run("SELECT count(*) AS n FROM devices WHERE user_id = %s", (user_id,), fetch="one")["n"]