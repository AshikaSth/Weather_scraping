import re

def parse_float(value):
    """Strip units and symbols then convert to float or return None."""
    if not value or value == 'N/A':
        return None
    cleaned = re.sub(r'[^\d.-]', '', value)
    try:
        return float(cleaned)
    except ValueError:
        return None

def parse_wind(value):
    """Parse '12 km/h NE' into (12.0, 'NE')"""
    if not value:
        return None, None
    speed_match = re.search(r'[\d.]+', value)
    speed = float(speed_match.group()) if speed_match else None

    parts = value.strip().split()
    direction = next((p for p in reversed(parts) if p.isalpha()), None)
    return speed, direction