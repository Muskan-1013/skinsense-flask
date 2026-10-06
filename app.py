"""SkinSense entry point.  Run locally:  python app.py   |  Deploy:  gunicorn app:app"""

import os

from flask import Flask

import database
from config import Config
from routes import bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    database.init_db(app)
    app.register_blueprint(bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))