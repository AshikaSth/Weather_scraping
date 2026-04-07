from sqlalchemy import func
from app import db

class WeatherRecord(db.Model):
    __tablename__ = 'weather_records'

    id                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city              = db.Column(db.String(100), nullable=False)
    scraped_at        = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    task_id           = db.Column(db.String(36), nullable=False)
    temperature       = db.Column(db.Float, nullable=False, default=0.0)
    real_feel         = db.Column(db.Float, nullable=False, default=0.0)
    weather_condition = db.Column(db.String(255), nullable=False, default="")
    humidity          = db.Column(db.Float, nullable=False, default=0.0)
    wind_speed        = db.Column(db.Float, nullable=False, default=0.0)
    wind_direction    = db.Column(db.String(10), nullable=False, default="")
    visibility        = db.Column(db.Float, nullable=False, default=0.0)
    max_uv_index      = db.Column(db.Float, nullable=False, default=0.0)
    dew_point         = db.Column(db.Float, nullable=False, default=0.0)
    pressure          = db.Column(db.Float, nullable=False, default=0.0)
    cloud_cover       = db.Column(db.Float, nullable=False, default=0.0)
    cloud_ceiling     = db.Column(db.Float, nullable=False, default=0.0)
    precipitation     = db.Column(db.Float, nullable=False, default=0.0)
    rain              = db.Column(db.Float, nullable=False, default=0.0)