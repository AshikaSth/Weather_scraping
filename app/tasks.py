import os
from celery import Celery
from celery.schedules import crontab

celery_app= Celery('weather',
                    broker = os.getenv('REDIS_URL', 'redis://redis:6379/0'),
                    backend = os.getenv('REDIS_URL', 'redis://redis:6379/0'))

celery_app.conf.beat_schedule = {
    'scrape-every-6-hour': {
        'task': 'app.tasks.scrape_weather',
        'schedule': crontab(minute=0, hour='*')
    }
}

@celery_app.task
def scrape_weather():
    from app.create import scrape_accuweather
    from app.main import save_to_db
    print("Starting weather scrape task...")
    data= scrape_accuweather()
    if data:
        print("Scraped data:", data)
        save_to_db(data)
    else:
        print("Failed to scrape weather data.")

# @celery_app.task
# def run_analysis():
#     # your analysis logic here
#     pass