import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from app.config import USER_AGENT, HEADLESS, IMPLICIT_WAIT, PAGE_SLEEP, DEFAULT_CITY_URL
from datetime import datetime

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
    if not value or value == None:
        return None, None
    speed_match = re.search(r'[\d.]+', value)
    speed = float(speed_match.group()) if speed_match else None

    parts = value.split()
    direction = parts[0] if parts[0].isalpha() else None
    return speed, direction

def get_driver():
    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080") 
    options.add_argument(f"user-agent={USER_AGENT}")

    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)    
    driver.implicitly_wait(IMPLICIT_WAIT)
    return driver

def scrape_accuweather(city_url=DEFAULT_CITY_URL):
    driver = get_driver()

    try:
        print(f"Loading: {city_url}")
        driver.get(city_url)
        time.sleep(PAGE_SLEEP) #let JS fully render

        soup = BeautifulSoup(driver.page_source.encode('utf-8'), "html.parser")

        weather_data = {
            "city": "Kathmandu",
            "scraped_at": datetime.now(),
            "temperature": None,
            "real_feel": None,
            "weather_condition": None,
            "humidity": None,
            "wind_speed": None,
            "wind_direction": None,
            "visibility": None,
            "max_uv_index": None,
        }

        # Current temp         
        temp_elem = soup.find('div', class_='display-temp')
        if temp_elem: weather_data['temperature'] = parse_float(temp_elem.text)

        #general weather condition like "Cloudy", "Sunny", etc
        cond_elem = soup.find('div', class_ = 'phrase')
        if cond_elem: weather_data['weather_condition'] = cond_elem.text.strip()

        #feels like temp
        extra_div = soup.find('div', class_ = 'current-weather-extra')
        if extra_div:
            full_text = extra_div.get_text(strip=True)
            match = re.search(r'RealFeel[^\d]*([\d,-]+°)', full_text)
            if match:
                realfeel = match.group(1)
        if realfeel: weather_data['real_feel'] = parse_float(realfeel)

        details_container = soup.find('div', class_=['current-weather-details', 'no-realfeel-phrase']) 
        if details_container:
            items = details_container.find_all('div', class_=['detail-item'])

        for item in items:
            divs = item.find_all('div', recursive=False)
            if len(divs) < 2:
                    continue
            label = divs[0].get_text(strip=True)
            value = divs[1].get_text(strip=True)

            # Logic-based mapping to your SQLAlchemy columns
            if "Humidity" in label:
                weather_data['humidity'] = parse_float(value)
            elif "Wind" in label and "Gusts" not in label:
                speed, direction = parse_wind(value)
                weather_data['wind_speed'] = speed
                weather_data['wind_direction'] = direction
            elif "Visibility" in label:
                weather_data['visibility'] = parse_float(value)
            elif "UV" in label:
                weather_data['max_uv_index'] = parse_float(value)

        return weather_data
    except Exception as e:
        print(f"Scraping error: {e}")
        return None
    finally: 
        driver.quit()
