import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()  # Charge .env en local (ignoré si les variables sont déjà définies)

# --- Extensions ---
db            = SQLAlchemy()
login_manager = LoginManager()
csrf          = CSRFProtect()
migrate_ext   = Migrate()

login_manager.login_view    = 'login'
login_manager.login_message = 'Connecte-toi pour accéder à cette page.'


def create_app() -> Flask:
    app = Flask(__name__)

    # --- Config ---
    secret_key = os.environ.get('SECRET_KEY', 'dev-only')
    if secret_key in ('dev-only', '', None):
        import warnings
        warnings.warn('SECRET_KEY non définie ou faible — ne pas déployer en production !', stacklevel=2)
    app.config['SECRET_KEY']                     = secret_key
    app.config['SQLALCHEMY_DATABASE_URI']        = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'orthoquizz.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ADMIN_LOGIN']                    = os.environ.get('ADMIN_LOGIN', 'admin')
    app.config['ADMIN_PASSWORD']                 = os.environ.get('ADMIN_PASSWORD', 'changeme')
    app.config['PHRASES_CSV']                    = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'phrases.csv')

    # --- Sécurité cookies session ---
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE']   = os.environ.get('FLASK_ENV') == 'production'

    # --- Init extensions ---
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate_ext.init_app(app, db)

    # --- Headers de sécurité HTTP ---
    is_production = os.environ.get('FLASK_ENV') == 'production'

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Frame-Options']        = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy']        = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://raw.githubusercontent.com https://pokeapi.co; "
            "connect-src 'self';"
        )
        response.headers['Permissions-Policy'] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), fullscreen=(self)"
        )
        if is_production:
            response.headers['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains'
            )
        return response

    # --- Routes ---
    from routes import register_routes
    register_routes(app)

    import models

    return app


# Exposé pour PythonAnywhere : from app import app as application
app = create_app()
