import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from app.config import USER_AGENT, HEADLESS, IMPLICIT_WAIT, PAGE_SLEEP, DEFAULT_CITY_URL
from datetime import datetime, timezone
from app.utils.parse import parse_float, parse_wind
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


logger = logging.getLogger(__name__)
def get_driver():
    options = Options()

    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080") 
    options.add_argument(f"user-agent={USER_AGENT}")

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)    
    driver.implicitly_wait(IMPLICIT_WAIT)
    return driver

def scrape_accuweather(city_url=DEFAULT_CITY_URL):
    driver = get_driver()

    try:
        print(f"Loading: {city_url}")
        driver.get(city_url)
        time.sleep(PAGE_SLEEP) 

        soup = BeautifulSoup(driver.page_source.encode('utf-8'), "html.parser")
        weather_data = {
            "city": "Kathmandu",
            "scraped_at": datetime.now(timezone.utc),
            "temperature": 0.0,
            "real_feel": 0.0,
            "weather_condition": "",
            "humidity": 0.0,
            "wind_speed": 0.0,
            "wind_direction": "",
            "visibility": 0.0,
            "max_uv_index": 0.0,
            "dew_point": 0.0,
            "pressure": 0.0,
            "cloud_cover": 0.0,
            "cloud_ceiling":0.0,
            "precipitation": 0.0,
            "rain": 0.0
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
                weather_data['real_feel'] = parse_float(match.group(1))

        items= soup.select('.current-weather-details .detail-item')
        for item in items:
            divs = item.find_all('div', recursive=False)

            if len(divs) >= 2:
                label = divs[0].get_text(strip=True)
                value = divs[1].get_text(strip=True)
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
                elif "Dew Point" in label:
                    weather_data['dew_point'] = parse_float(value)
                elif "Pressure" in label:
                    weather_data['pressure'] = parse_float(value)
                elif "Cloud Cover" in label:
                    weather_data['cloud_cover'] = parse_float(value)
                elif "Cloud Ceiling" in label:
                    weather_data['cloud_ceiling'] = parse_float(value)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".half-day-card"))
        )        
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        panels = soup.select('.half-day-card .panel-item')

        cards = soup.select('.half-day-card')

        if cards:
            day_card = cards[0]  
            panels = day_card.select('.panel-item')
        else:
            panels = []
        logger.warning(f"half-day-card exists: {bool(soup.select_one('.half-day-card'))}")
        logger.warning(f"panel-item count: {len(soup.select('.panel-item'))}")
        logger.warning(f"Processing ONLY day card panels: {len(panels)}")

        for panel in panels:
            logger.warning(f"PANEL RAW: {panel.get_text(strip=True)}")
            text = panel.get_text(strip=True)

            if "mm" not in text:
                continue
            if "Precipitation" in text:
                    mm = extract_mm(text)
                    if mm is not None:
                        weather_data['precipitation'] = mm

            elif "Rain" in text:
                mm = extract_mm(text)
                if mm is not None:
                    weather_data['rain'] = mm

        for key, value in weather_data.items():
            if value is None:
                if isinstance(value, str):
                    weather_data[key] = ""
                else:
                    weather_data[key] = 0.0

        return weather_data
    except Exception as e:
        print(f"Scraping error: {e}")
        return None
    finally: 
        driver.quit()

import re
def extract_mm(text):
    match = re.search(r"(\d+(\.\d+)?)\s*mm", text)
    return float(match.group(1)) if match else None