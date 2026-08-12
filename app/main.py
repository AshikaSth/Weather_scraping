from app import create_app, db
from app.analytics.analysis import load_data, prepare_visibility, get_chart_data, get_humidity_visibility_data
from app.analytics.insights import generate_insight          # ← new home
from app.analytics.clean import clean_data
from app.models.weather import WeatherRecord
from flask import render_template, redirect, url_for, request, jsonify
from datetime import timezone, timedelta
import json
import os

app = create_app()
nepal_tz = timezone(timedelta(hours=5, minutes=45))

@app.route('/')
def dashboard():
    records = WeatherRecord.query.order_by(WeatherRecord.scraped_at.desc()).all()
    for record in records:
        if record.scraped_at:
            record.scraped_at = record.scraped_at.replace(tzinfo=timezone.utc).astimezone(nepal_tz)
    return render_template('dashboard.html', weather_records=records)

@app.route('/analysis')
def analysis():
    # Get chart data (Chart.js compatible)
    chart_data = get_chart_data()
    
    # Generate AI insight (falls back gracefully if API is down)
    df_raw = clean_data()
    df_vis = prepare_visibility(df_raw)
    insight = generate_insight(df_vis)
    
    return render_template(
        "analysis.html",
        chart_data_json=json.dumps(chart_data),
        insight=insight,
    )

@app.route('/api/chart-data')
def api_chart_data():
    """API endpoint to fetch chart data as JSON"""
    return jsonify(get_chart_data())

@app.route('/api/humidity-visibility')
def api_humidity_visibility():
    """API endpoint to fetch chart data as JSON"""
    return jsonify(get_humidity_visibility_data())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)