"""All page routes, grouped in one blueprint."""

from flask import Blueprint, redirect, render_template, request, session

import content
import database
from analysis import analyse
from auth import (
    hash_password, is_valid_email, login_required, normalize_email,
    password_error, verify_password,
)
from config import Config
from models import Reading

bp = Blueprint("main", __name__)


# ---------- public pages ----------

@bp.route("/")
def home():
    return render_template("home.html", features=content.features, steps=content.steps)


@bp.route("/product")
def product():
    return render_template(
        "product.html", specs=content.specs, comparison=content.comparison, readings=content.readings
    )


@bp.route("/how-it-works")
def how_it_works():
    return render_template("how-it-works.html", readings=content.readings)


@bp.route("/science")
def science():
    return render_template("science.html", calibrations=content.calibrations)


@bp.route("/insights")
def insights():
    return render_template(
        "insights.html", skin_types=content.skin_types, ingredients=content.ingredients
    )


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/analyze", methods=["GET", "POST"])
def analyze():
    """Enter three readings by hand and see the engine's result."""
    profile, error, values = None, "", {}
    if request.method == "POST":
        values = request.form
        try:
            profile = analyse(Reading.from_form(request.form))
        except ValueError as problem:
            error = str(problem)
    return render_template("analyze.html", profile=profile, error=error, values=values)


# ---------- forms ----------

@bp.route("/contact", methods=["GET", "POST"])
def contact():
    message, status = "", "ok"
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = normalize_email(request.form.get("email"))
        text = request.form.get("message", "").strip()
        if not name or not text:
            message, status = "Please fill in every field.", "err"
        elif not is_valid_email(email):
            message, status = "Please enter a valid email address.", "err"
        elif len(text) > Config.MAX_MESSAGE_LENGTH:
            message, status = "Message is too long.", "err"
        else:
            database.add_contact(name, email, text)
            message = "Thank you, %s. We will reply to %s soon." % (name, email)
    return render_template("contact.html", message=message, status=status)


@bp.route("/waitlist", methods=["GET", "POST"])
def waitlist():
    message, status = "", "ok"
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = normalize_email(request.form.get("email"))
        skintype = request.form.get("skintype", "").strip()[:40]
        if not name:
            message, status = "Please enter your name.", "err"
        elif not is_valid_email(email):
            message, status = "Please enter a valid email address.", "err"
        elif database.add_waitlist(name, email, skintype):
            message = "You are on the list, %s!" % name
        else:
            message = "That email is already on the waitlist."
    return render_template("waitlist.html", message=message, status=status)


# ---------- accounts ----------

@bp.route("/signup", methods=["GET", "POST"])
def signup():
    message = ""
    if request.method == "POST":
        email = normalize_email(request.form.get("email"))
        password = request.form.get("password", "")
        if not is_valid_email(email):
            message = "Please enter a valid email address."
        elif password_error(password):
            message = password_error(password)
        elif database.create_user(email, hash_password(password)) is None:
            message = "This email is already registered."
        else:
            session.clear()
            session["user"] = email
            return redirect("/account")
    return render_template("signup.html", message=message, min_length=Config.MIN_PASSWORD_LENGTH)


@bp.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        email = normalize_email(request.form.get("email"))
        password = request.form.get("password", "")
        user = database.get_user_by_email(email)
        if user is not None and verify_password(user["password_hash"], password):
            session.clear()
            session["user"] = email
            return redirect("/account")
        message = "Invalid email or password."
    return render_template("login.html", message=message)


@bp.route("/account")
@login_required
def account():
    return render_template("account.html", user=session["user"])


@bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")