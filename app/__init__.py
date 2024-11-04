from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from datetime import datetime
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()  # Créez une instance de Migrate
mail = Mail()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)  # Initialisez Migrate correctement
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow}

    with app.app_context():
        from . import routes  # Importez les routes ici
        db.create_all()  # Créez les tables si elles n'existent pas

    return app