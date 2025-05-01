"""
Production‑ready single‑file Flask app
  • Env‑based config (SECRET_KEY required)
  • CSRF protection
  • Security headers (HSTS, CSP, etc.)
  • No database — renders Jinja templates only
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_wtf import CSRFProtect
from flask_talisman import Talisman

# ---------------------------------------------------------------------------#
# 1.  Environment variables (dotenv only for local dev)                      #
# ---------------------------------------------------------------------------#
BASE_DIR = Path(__file__).resolve().parent
if os.getenv("FLASK_ENV") == "development":
    load_dotenv(BASE_DIR / ".env", override=False)

class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]                 # must be set
    SESSION_COOKIE_SECURE   = True                        # HTTPS‑only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_TIME_LIMIT     = 3600                        # 1 hour

# ---------------------------------------------------------------------------#
# 2.  Factory & routes                                                       #
# ---------------------------------------------------------------------------#
def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)

    # -- Security extensions -------------------------------------------------
    CSRFProtect(app)
    csp = {
        "default-src": ["'self'"],
        "img-src":     ["'self'", "data:"],
        "style-src":   ["'self'", "'unsafe-inline'"],
        "script-src":  ["'self'"],
    }
    Talisman(app, content_security_policy=csp, force_https=True)

    # -- Public routes -------------------------------------------------------
    @app.route("/")
    def home():
        return render_template('index1.html')

    @app.route("/products")
    def products():
        return "products"

    @app.route("/about")
    def about():
        return render_template('about.html')
    # Health check for Render / LB probes
    @app.route("/healthz")
    def healthz():
        return {"status": "ok"}, 200

    return app

# ---------------------------------------------------------------------------#
# 3.  WSGI entry‑point for Gunicorn / Render                                 #
# ---------------------------------------------------------------------------#
app = create_app()          # Render & Gunicorn import this object
