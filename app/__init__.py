from flask import Flask
from app.extensions import db, login_manager, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.images import images_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(images_bp)

    # User loader function
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app