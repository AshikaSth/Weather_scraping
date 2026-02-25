from flask import Flask, render_template
from app.database import get_db_session
from app.models.weather import WeatherRecord

app = Flask(__name__)

@app.route('/')
def dashboard():
    session = get_db_session()
    try:
        # Fetch the 20 most recent records
        records = session.query(WeatherRecord).order_by(WeatherRecord.scraped_at.desc()).limit(20).all()
        return render_template('dashboard.html', weather_records=records)
    finally:
        session.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)