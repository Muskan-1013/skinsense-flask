"""SQLite storage: connection handling, versioned migrations and queries."""

import os
import sqlite3

from flask import current_app, g

from auth import hash_password

# Each entry upgrades the schema by one version (tracked with PRAGMA user_version).
MIGRATIONS = [
    """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE waitlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        skintype TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """,
]


# ---------- connection handling ----------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def run_migrations(db):
    version = db.execute("PRAGMA user_version").fetchone()[0]
    for number in range(version, len(MIGRATIONS)):
        db.executescript(MIGRATIONS[number])
        db.execute("PRAGMA user_version = %d" % (number + 1))
    db.commit()


def init_db(app):
    """Create/upgrade the schema and import any old .txt data. Call once at startup."""
    app.teardown_appcontext(close_db)
    with app.app_context():
        db = get_db()
        run_migrations(db)
        import_legacy_files(db, app.config["LEGACY_FILES"])


# ---------- one-time import of the old text files ----------

def _read_lines(path):
    if not os.path.exists(path):
        return None
    with open(path, "r") as file:
        return [line.rstrip("\n") for line in file if line.strip()]


def import_legacy_files(db, paths):
    """Import users.txt, contacts.txt and waitlist.txt, then rename them.

    Old passwords were stored in plain text, so each one is hashed on import.
    """
    lines = _read_lines(paths["users"])
    if lines is not None:
        for line in lines:
            email, _, password = line.partition(",")
            if email and password:
                db.execute(
                    "INSERT OR IGNORE INTO users (email, password_hash) VALUES (?, ?)",
                    (email.strip().lower(), hash_password(password)),
                )
        os.rename(paths["users"], paths["users"] + ".migrated")

    lines = _read_lines(paths["contacts"])
    if lines is not None:
        for line in lines:
            parts = line.split(",", 2)  # message may contain commas
            if len(parts) == 3:
                db.execute("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)", parts)
        os.rename(paths["contacts"], paths["contacts"] + ".migrated")

    lines = _read_lines(paths["waitlist"])
    if lines is not None:
        for line in lines:
            parts = (line.split(",") + ["", ""])[:3]
            if parts[0] and parts[1]:
                db.execute(
                    "INSERT OR IGNORE INTO waitlist (name, email, skintype) VALUES (?, ?, ?)",
                    (parts[0], parts[1].strip().lower(), parts[2]),
                )
        os.rename(paths["waitlist"], paths["waitlist"] + ".migrated")
    db.commit()


# ---------- queries ----------

def create_user(email, password_hash):
    """Insert a user. Returns the new id, or None if the email already exists."""
    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password_hash)
        )
        db.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None


def get_user_by_email(email):
    return get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def add_contact(name, email, message):
    db = get_db()
    db.execute("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)", (name, email, message))
    db.commit()


def add_waitlist(name, email, skintype):
    """Returns True if added, False if the email was already on the list."""
    db = get_db()
    try:
        db.execute(
            "INSERT INTO waitlist (name, email, skintype) VALUES (?, ?, ?)", (name, email, skintype)
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False