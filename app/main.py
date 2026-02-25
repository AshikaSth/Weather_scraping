from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.weather import Base, WeatherRecord
from app.create import scrape_accuweather
import os

def get_db_session():
    host = os.getenv('MYSQL_HOST')
    user = os.getenv('MYSQL_USER')
    db = os.getenv('MYSQL_DB')
    password = os.getenv('MYSQL_PASSWORD')
    print(f"DEBUG - Connecting to DB at {host} with user {user} and db {db}")
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


if __name__=="__main__":
    data = scrape_accuweather()
    if data:
        print("===Weather in Kathmandu===")
        print(f"Scraped At:  {data.get('scraped_at')}")
        print(f"City:        {data.get('city')}")
        print(f"Temperature: {data.get('temperature', 'N/A')}")
        print(f"Feels Like: {data.get('real_feel', 'N/A')}")
        print(f"Condition: {data.get('condition', 'N/A')}")
        print(f"Humidity: {data.get('humidity', 'N/A')}")        
        print(f"Wind: {data.get('wind', 'N/A')}")
        print(f"Max UV Index: {data.get('max_uv_index', 'N/A')}")
        # print(f"Precipitation: {data.get('precipitation', 'N/A')}")
        # print(f"Rain:")
        print("==================")
        save_to_db(data)
    else: 
        print("Failed to scrape weather data.")
