import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()  # Charge .env en local (ignoré si les variables sont déjà définies)

# --- Extensions ---
db            = SQLAlchemy()
#login_manager = LoginManager()
csrf          = CSRFProtect()

#login_manager.login_view    = 'login'
#login_manager.login_message = 'Connecte-toi pour accéder à cette page.'


def create_app() -> Flask:
    app = Flask(__name__)

    # --- Config ---
    app.config['SECRET_KEY']                     = os.environ.get('SECRET_KEY', 'dev-only')
    app.config['SQLALCHEMY_DATABASE_URI']        = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'orthoquizz.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ADMIN_LOGIN']                    = os.environ.get('ADMIN_LOGIN', 'admin')
    app.config['ADMIN_PASSWORD']                 = os.environ.get('ADMIN_PASSWORD', 'changeme')
    app.config['PHRASES_CSV']                    = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'phrases.csv')

    # --- Init extensions ---
    db.init_app(app)
    #login_manager.init_app(app)
    csrf.init_app(app)

    # --- Routes ---
    from routes import register_routes
    register_routes(app)

    return app


# Exposé pour PythonAnywhere : from app import app as application
app = create_app()
