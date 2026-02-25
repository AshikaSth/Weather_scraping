
def print_weather_report(data):
    """Helper to print formatted weather data to the console."""
    if not data:
        print("No weather data available to print.")
        return

    print("\n=== Weather Report: Kathmandu ===")
    print(f"Scraped At:    {data.get('scraped_at')}")
    print(f"Condition:     {data.get('weather_condition', 'N/A')}")
    print(f"Temperature:   {data.get('temperature', 'N/A')}°C")
    print(f"Feels Like:    {data.get('real_feel', 'N/A')}°C")
    print(f"Humidity:      {data.get('humidity', 'N/A')}%")
    print(f"Wind Speed:    {data.get('wind_speed', 'N/A')} km/h")
    print(f"Wind Direction:{data.get('wind_direction', 'N/A')}")
    print(f"Pressure:      {data.get('pressure', 'N/A')} mb")
    print(f"Visibility:    {data.get('visibility', 'N/A')} km")
    print(f"Cloud Cover:   {data.get('cloud_cover', 'N/A')}%")
    print(f"Cloud Ceiling: {data.get('cloud_ceiling', 'N/A')} m")
    print(f"Max UV Index:  {data.get('max_uv_index', 'N/A')}")
    print("=================================\n")