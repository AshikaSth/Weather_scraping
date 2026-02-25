from dotenv import load_dotenv
import os
load_dotenv()

# Browser / Selenium config
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
IMPLICIT_WAIT = float(os.getenv("IMPLICIT_WAIT", "10"))
PAGE_SLEEP = float(os.getenv("PAGE_LOAD_SLEEP", "5"))

# AccuWeather URLs
BASE_URL = os.getenv("WEATHER_BASE_URL", "https://www.accuweather.com/")
KTM_DETAIL_PATH = os.getenv("KATHMANDU_DETAIL_URL", "/en.np/kathmandu/241809/current-weather/241809")
DEFAULT_CITY_URL = f"{BASE_URL}{KTM_DETAIL_PATH}"