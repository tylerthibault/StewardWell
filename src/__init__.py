"""
StewardWell Flask application package

Provides the application factory (create_app) and shared extensions (db, login_manager).
"""

from __future__ import annotations

import config
from flask import Flask
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Extensions (available for import as `from src import db`)
db: SQLAlchemy = SQLAlchemy()
login_manager: LoginManager = LoginManager()


def create_app() -> Flask:
    """Application factory for StewardWell.

    Returns:
        Flask: Configured Flask application instance.
    """
    # NOTE: When using a package (__name__ == 'src'), template/static paths
    # are relative to the package root. Our folders live at src/templates and
    # src/static, so we pass just 'templates' and 'static' here.
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static',
    )

    # Base configuration
    app.config.update(
        SECRET_KEY=config.SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=config.DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=config.SQLALCHEMY_TRACK_MODIFICATIONS,
    )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id: str):  # noqa: ANN001 - signature required by Flask-Login
        # Lazy import to avoid circular imports
        from src.models.user_model import User
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Register blueprints (lazy imports to avoid circular dependencies)
    from src.controllers.main import main_bp
    # Some projects prefer `auth_controller.py`; try both import paths safely
    try:
        from src.controllers.auth_controller import auth_bp  # type: ignore
    except Exception:
        from src.controllers.auth import auth_bp  # type: ignore
    from src.controllers.family_controller import family_bp
    from src.controllers.child_controller import child_bp
    from src.controllers.store_controller import store_bp
    from src.controllers.chores_controller import chores_bp
    from src.controllers.family_management_controller import family_mgmt_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(child_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(chores_bp)
    app.register_blueprint(family_mgmt_bp)

    # Lightweight SQLite schema patches (non-destructive):
    # Ensure newer columns exist when working with an older local DB file.
    # This avoids crashes like "no such column: individual_reward.is_infinite".
    if isinstance(app.config.get('SQLALCHEMY_DATABASE_URI'), str) and 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
        with app.app_context():
            def ensure_column(table: str, column: str, column_def: str) -> None:
                try:
                    result = db.session.execute(text(f"PRAGMA table_info({table})"))
                    cols = {row[1] for row in result}  # row[1] is the column name
                    if column not in cols:
                        db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {column_def}"))
                        db.session.commit()
                except Exception:
                    # Don't block app startup on a best-effort patch
                    db.session.rollback()

            # Add any incremental columns here
            ensure_column('individual_reward', 'is_infinite', 'INTEGER NOT NULL DEFAULT 0')
            ensure_column('family_reward', 'is_infinite', 'INTEGER NOT NULL DEFAULT 0')
            ensure_column('family', 'family_points', 'INTEGER NOT NULL DEFAULT 0')
            ensure_column('chore', 'assigned_user_id', 'INTEGER')

    return app


__all__ = [
    'create_app',
    'db',
    'login_manager',
]
