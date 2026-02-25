import os
from celery import Celery
from celery.schedules import crontab
from utils.common import print_weather_report
celery_app= Celery('weather',
                    broker = os.getenv('REDIS_URL', 'redis://redis:6379/0'),
                    backend = os.getenv('REDIS_URL', 'redis://redis:6379/0'))

celery_app.conf.beat_schedule = {
    'scrape-every-6-hour': {
        'task': 'app.tasks.scrape_weather',
        'schedule': crontab(minute=0, hour='*')
    }
}

@celery_app.task(bind=True)
def scrape_weather(self):
    from app.create import scrape_accuweather
    from app.database import save_to_db
    task_id = self.request.id
    print(f"Starting weather scrape task {task_id}...")
    data = scrape_accuweather()
    if data:
        data['task_id'] = task_id
        print_weather_report(data)
        save_to_db(data)
    else:
        print("Failed to scrape weather data.")

# @celery_app.task
# def run_analysis():
#     # your analysis logic here
#     pass