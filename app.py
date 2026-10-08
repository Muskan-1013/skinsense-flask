"""SkinSense entry point.  Run locally:  python app.py   |  Deploy:  gunicorn app:app"""

import os

from flask import Flask

import database
from config import Config
from extensions import csrf, limiter
from routes import bp
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app(config_class=Config):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)  # one proxy in front (Render, Railway, Heroku)
    app.config.from_object(config_class)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY is not set")
    database.init_db(app)
    csrf.init_app(app)
    limiter.init_app(app)
    app.register_blueprint(bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))