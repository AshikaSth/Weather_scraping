from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class WeatherRecord(Base):
    __tablename__ = 'weather_records'

    id                = Column(Integer, primary_key=True, autoincrement=True)
    city              = Column(String(100), nullable=False)
    scraped_at        = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    temperature       = Column(Float)
    real_feel         = Column(Float)
    weather_condition = Column(String(255))
    humidity          = Column(Float)
    wind_speed        = Column(Float)
    wind_direction    = Column(String(10))
    visibility        = Column(Float)
    max_uv_index      = Column(Float)
    dew_point         = Column(Float)
    pressure          = Column(Float)
    cloud_cover       = Column(Float)
    cloud_ceiling     = Column(Float)
    task_id           = Column(String(36))