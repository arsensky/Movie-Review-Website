from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from config import Config


db = SQLAlchemy()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    csrf.init_app(app)

    from app.routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        from app import models  # noqa: F401
        from app.poster_utils import ensure_runtime_dirs
        from app.seed import seed_default_data

        ensure_runtime_dirs()
        db.create_all()
        seed_default_data()

    return app
