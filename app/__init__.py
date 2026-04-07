from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER', 'user')}:{os.getenv('MYSQL_PASSWORD', 'password')}@{os.getenv('MYSQL_HOST', 'db')}/{os.getenv('MYSQL_DB', 'weather_db')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db) 
    return app