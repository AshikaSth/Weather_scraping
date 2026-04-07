# app/database.py
from app import db
from app.models.weather import WeatherRecord

def save_to_db(data):
    try:
        record = WeatherRecord(**data)
        db.session.add(record)
        db.session.commit()
        print("Saved to DB successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"DB error: {e}")