from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from config import Config

db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()

csrf = CSRFProtect()

limiter = Limiter(
    key_func=get_remote_address
)

def create_app():
    
    flask_app = Flask(__name__)

    Talisman(
        flask_app,
        content_security_policy=None
    )

    flask_app.config.from_object(Config)

    db.init_app(flask_app)

    migrate.init_app(flask_app, db)

    login_manager.init_app(flask_app)

    login_manager.login_view = 'auth.login'

    csrf.init_app(flask_app)

    limiter.init_app(flask_app)

    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.entrada_routes import entrada_bp
    from app.routes.salida_routes import salida_bp
    from app.routes.usuario_routes import usuario_bp
    from app.routes.mensajeria_routes import mensajeria_bp
    
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(dashboard_bp)
    flask_app.register_blueprint(entrada_bp)
    flask_app.register_blueprint(salida_bp)
    flask_app.register_blueprint(usuario_bp)
    flask_app.register_blueprint(mensajeria_bp)
    return flask_app


from app.models.usuario import Usuario


@login_manager.user_loader
def load_user(user_id):

    return Usuario.query.get(int(user_id))