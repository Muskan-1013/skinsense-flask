# app.py
# SkinSense website using Flask
# Uses only Python concepts from the syllabus

from flask import Flask, render_template, request, redirect, session
import os

app = Flask(__name__)
app.secret_key = "skinsense_secret_key_2026"


# ============ DATA (LISTS AND DICTIONARIES) ============

features = [
    {"icon": "M", "title": "Moisture", "text": "Capacitive sensing detects hydration."},
    {"icon": "pH", "title": "pH Balance", "text": "Liquid pH probe reads acid-alkaline state."},
    {"icon": "O", "title": "Oiliness", "text": "Blotting paper and light sensor quantify sebum."},
    {"icon": "I", "title": "Ingredient Guidance", "text": "Decision-tree algorithm suggests ingredients."}
]

steps = [
    "Press the sensors against your skin",
    "Get instant readings on the LCD",
    "Receive ingredient suggestions"
]

specs = [
    ("Controller", "ESP32"),
    ("Moisture Sensor", "YL-69"),
    ("pH Sensor", "PH-4502C"),
    ("Light Sensor", "BH1750"),
    ("Display", "16x2 LCD"),
    ("Estimated Cost", "Rs. 2,500")
]

comparison = [
    ("VISIA Complexion", "14+", "4.2L - 16.8L"),
    ("HiMirror", "3", "8.4K - 25K"),
    ("Neutrogena Skin360", "3", "Free"),
    ("DermaSense", "3", "~2.5K")
]

skin_types = [
    {"type": "Oily", "condition": "Oiliness greater than 60%"},
    {"type": "Dry", "condition": "Oiliness less than 20% and Moisture less than 40%"},
    {"type": "Combination", "condition": "Oiliness between 20% and 60%"},
    {"type": "Normal", "condition": "Oiliness 20-60% and Moisture greater than 40%"}
]

ingredients = [
    {"type": "Dry", "list": "Hyaluronic Acid, Glycerin, Ceramides"},
    {"type": "Oily", "list": "Niacinamide, Salicylic Acid, Zinc PCA"},
    {"type": "Combination", "list": "Lactic Acid, Vitamin B5"},
    {"type": "Normal", "list": "Vitamin C, Peptides"}
]

readings = [
    {"name": "Moisture", "meaning": "Low <40%: Dry. Normal 40-70%: Balanced. High >70%: Well-hydrated."},
    {"name": "pH", "meaning": "Healthy 4.5-5.8: Barrier intact. Acidic <4.5: Irritation. Alkaline >5.8: Compromised."},
    {"name": "Oiliness", "meaning": "Low <20%: Dry. Medium 20-60%: Normal. High >60%: Oily."}
]

calibrations = [
    {"name": "Moisture", "detail": "Two-point calibration on dry and wet skin. Range: 236 ADC units."},
    {"name": "pH", "detail": "Calibrated with pH 4.0 and pH 9.0 buffers. R-squared = 0.999."},
    {"name": "Oiliness", "detail": "Calibrated with clean and oil-saturated blotting paper. Range: 600 lux."}
]


# ============ FILE HANDLING FUNCTIONS ============

def load_users():
    users = {}
    try:
        file = open("users.txt", "r")
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 2:
                users[parts[0]] = parts[1]
        file.close()
    except FileNotFoundError:
        pass
    return users


def save_user(email, password):
    file = open("users.txt", "a")
    file.write(email + "," + password + "\n")
    file.close()


def save_contact(name, email, message):
    file = open("contacts.txt", "a")
    file.write(name + "," + email + "," + message + "\n")
    file.close()


def save_waitlist(name, email, skintype):
    file = open("waitlist.txt", "a")
    file.write(name + "," + email + "," + skintype + "\n")
    file.close()


# ============ ROUTES ============

@app.route("/")
def home():
    return render_template("home.html", features=features, steps=steps)


@app.route("/product")
def product():
    return render_template("product.html", specs=specs, comparison=comparison, readings=readings)


@app.route("/how-it-works")
def how_it_works():
    return render_template("how-it-works.html", readings=readings)


@app.route("/science")
def science():
    return render_template("science.html", calibrations=calibrations)


@app.route("/insights")
def insights():
    return render_template("insights.html", skin_types=skin_types, ingredients=ingredients)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    message = ""
    if request.method == "POST":
        try:
            name = request.form["name"]
            email = request.form["email"]
            text = request.form["message"]
            save_contact(name, email, text)
            message = "Thank you, " + name + ". We will reply to " + email + " soon."
        except Exception as error:
            message = "Error: " + str(error)
    return render_template("contact.html", message=message)


@app.route("/waitlist", methods=["GET", "POST"])
def waitlist():
    message = ""
    if request.method == "POST":
        try:
            name = request.form["name"]
            email = request.form["email"]
            skintype = request.form.get("skintype", "")
            save_waitlist(name, email, skintype)
            message = "You are on the list, " + name + "!"
        except Exception as error:
            message = "Error: " + str(error)
    return render_template("waitlist.html", message=message)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    message = ""
    if request.method == "POST":
        try:
            email = request.form["email"]
            password = request.form["password"]
            users = load_users()
            if email in users:
                message = "This email is already registered."
            else:
                save_user(email, password)
                session["user"] = email
                return redirect("/account")
        except Exception as error:
            message = "Error: " + str(error)
    return render_template("signup.html", message=message)


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        try:
            email = request.form["email"]
            password = request.form["password"]
            users = load_users()
            if users.get(email) == password:
                session["user"] = email
                return redirect("/account")
            else:
                message = "Invalid email or password."
        except Exception as error:
            message = "Error: " + str(error)
    return render_template("login.html", message=message)


@app.route("/account")
def account():
    if "user" not in session:
        return redirect("/login")
    return render_template("account.html", user=session["user"])


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/signup")


# ============ START ============

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)