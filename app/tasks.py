import os
from celery import Celery
from celery.schedules import crontab
from app import create_app, db
from app.database import save_to_db

flask_app = create_app()

celery_app = Celery(
    'weather',
    broker=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://redis:6379/0')
)

celery_app.conf.beat_schedule = {
    'scrape-every-15-minutes': {
        'task': 'app.tasks.scrape_weather',
        'schedule': crontab(minute="*/15")
    }
}

@celery_app.task(bind=True)
def scrape_weather(self):
    from app.scraper.accuweather import scrape_accuweather
    task_id = self.request.id
    print(f"Starting weather scrape task {task_id}...")
    data = scrape_accuweather()
    if data:
        data['task_id'] = task_id
        print("Scraped data:", data)
        with flask_app.app_context():
            save_to_db(data)
    else:
        print("Failed to scrape weather data.")
# @celery_app.task
# def run_analysis():
#     # your analysis logic here
#     pass