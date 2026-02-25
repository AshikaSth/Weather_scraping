import pytz
from datetime import datetime
def get_local_time(utc_dt):
    """Converts a UTC datetime to Asia/Kathmandu time string."""
    if not utc_dt: return "N/A"
    nepal_tz = pytz.timezone('Asia/Kathmandu')
    # Localize if naive, then convert
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    return utc_dt.astimezone(nepal_tz).strftime('%Y-%m-%d %I:%M %p')