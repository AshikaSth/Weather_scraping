from flask import Flask, render_template
from database import get_db_session
from models.weather import WeatherRecord
from datetime import timezone, timedelta
app = Flask(__name__)
nepal_tz = timezone(timedelta(hours=5, minutes=45))

@app.route('/')
def dashboard():
    session = get_db_session()
    try:
        # Fetch the 20 most recent records
        records = session.query(WeatherRecord).order_by(WeatherRecord.scraped_at.desc()).all()
        for record in records:
            if record.scraped_at:
                record.scraped_at = record.scraped_at.replace(tzinfo=timezone.utc).astimezone(nepal_tz)
        return render_template('dashboard.html', weather_records=records)
    finally:
        session.close()


if __name__=="__main__":
   app.run(host='0.0.0.0', port=5000, debug=True)
