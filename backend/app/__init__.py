from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from datetime import timedelta

from .config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # JWT config
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        seconds=app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    )

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=[app.config["FRONTEND_URL"]], supports_credentials=True)

    # Import models so they are registered with SQLAlchemy
    from .models import user, document, purchase, payment  # noqa: F401

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.documents import documents_bp
    from .routes.payments import payments_bp
    from .routes.users import users_bp
    from .routes.ai import ai_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(documents_bp, url_prefix="/api/documents")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "OK"}

    return app
