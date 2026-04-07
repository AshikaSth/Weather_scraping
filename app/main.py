from app import create_app, db
from app.models.weather import WeatherRecord
from flask import render_template, redirect, url_for, request
from datetime import timezone, timedelta
import os, subprocess
app = create_app()
nepal_tz = timezone(timedelta(hours=5, minutes=45))

@app.route('/')
def dashboard():
    records = WeatherRecord.query.order_by(WeatherRecord.scraped_at.desc()).all()
    for record in records:
        if record.scraped_at:
            record.scraped_at = record.scraped_at.replace(tzinfo=timezone.utc).astimezone(nepal_tz)
    return render_template('dashboard.html', weather_records=records )

if __name__=="__main__":
   app.run(host='0.0.0.0', port=5000, debug=True)