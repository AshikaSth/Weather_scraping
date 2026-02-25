import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.weather import Base, WeatherRecord


def get_db_session():
    host = os.getenv('MYSQL_HOST')
    user = os.getenv('MYSQL_USER')
    db = os.getenv('MYSQL_DB')
    password = os.getenv('MYSQL_PASSWORD')
    url = f"mysql+pymysql://{user}:{password}@{host}/{db}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

def save_to_db(data):
    session = get_db_session()
    try:
        record = WeatherRecord(**data)
        session.add(record)
        session.commit()
        print("Saved to DB successfully.")
    except Exception as e:
        session.rollback()
        print(f"DB error: {e}")
    finally:
        session.close()
