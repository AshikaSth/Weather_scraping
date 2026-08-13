from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    postgres_user = os.environ["POSTGRES_USER"]
    postgres_password = os.environ["POSTGRES_PASSWORD"]
    postgres_host = os.environ["POSTGRES_HOST"]
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_db = os.environ["POSTGRES_DB"]

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg://"
        f"{postgres_user}:{postgres_password}@"
        f"{postgres_host}:{postgres_port}/"
        f"{postgres_db}"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    return app