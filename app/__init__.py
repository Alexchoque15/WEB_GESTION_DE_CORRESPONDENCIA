from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from config import Config

db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()


def create_app():

    flask_app = Flask(__name__)

    flask_app.config.from_object(Config)

    db.init_app(flask_app)

    migrate.init_app(flask_app, db)

    login_manager.init_app(flask_app)

    login_manager.login_view = 'auth.login'

    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.entrada_routes import entrada_bp
    from app.routes.salida_routes import salida_bp

    flask_app.register_blueprint(dashboard_bp)
    flask_app.register_blueprint(entrada_bp)
    flask_app.register_blueprint(salida_bp)

    return flask_app


from app.models.usuario import Usuario


@login_manager.user_loader
def load_user(user_id):

    return Usuario.query.get(int(user_id))