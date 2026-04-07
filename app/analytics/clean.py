# analytics/clean.py

from app import db
from app.models import WeatherRecord
import pandas as pd
def clean_data():
    """Load raw weather data from DB into dataframe and clean it step by step."""
    
    #load raw data
    records = WeatherRecord.query.all
    df = pd.DataFrame([{
        'id': r.id,
        'city': r.city,
        'scraped_at': r.scraped_at,
        'task_id': r.task_id,
        'temperature': r.temperature,
        'real_feel': r.real_feel,
        'weather_condition': r.weather_condition,
        'humidity': r.humidity,
        'wind_speed': r.wind_speed,
        'wind_direction': r.wind_direction,
        'visibility': r.visibility,
        'max_uv_index': r.max_uv_index,
        'dew_point': r.dew_point,
        'pressure': r.pressure,
        'cloud_cover': r.cloud_cover,
        'cloud_ceiling': r.cloud_ceiling,
        'precipitation': r.precipitation,
        'rain': r.rain
    }for r in records])

    # 1. Remove duplicates
    df = remove_duplicates(df)

    # 2. Handle outliers
    df = handle_outliers(df)
        
    # 3. Fill missing/placeholder numeric values
    df = fill_missing_numeric_values(df)

    # 4. Fill missing/placeholder string values
    df = fill_missing_value_for_strings(df)
    
    # 5. Standardize strings
    df= standardize_strings(df)

    # 6. Normalize datetime if needed
    normalize_datetime()

def remove_duplicates(df: pd.DataFrame):
    df_cleaned = df.drop_duplicates(subset=['task_id', 'city'], keep='first')
    df_cleaned.reset_index(drop=True, inplace=True)
    return df_cleaned

def handle_outliers(df):
    """Handle unrealistic values using domain rules."""

    rules = {
        'temperature': (-50, 60),
        'real_feel': (-50, 60),
        'humidity': (0, 100),
        'wind_speed': (0, 150),
        'visibility': (0, 50),
        'max_uv_index': (0, 15),
        'dew_point': (-50, 40),
        'pressure': (870, 1085),
        'cloud_cover': (0, 100),
        'cloud_ceiling': (0, 20000),
        'precipitation': (0, 500),
        'rain': (0, 500),
    }

    for col, (min_val, max_val) in rules.items():
        df.loc[(df[col] < min_val) | (df[col] > max_val), col] = pd.NA

    return df

def fill_missing_numeric_values(df: pd.DataFrame, method="median") -> pd.DataFrame:
    # fill zeros with median or mean

    cols_zero_invalid = {
        'temperature',
        'real_feel',
        'humidity',
        'visibility',
        'dew_point',
        'pressure',
        'cloud_cover',
        'cloud_ceiling'
    }

    for col in cols_zero_invalid:
        df[col] = df[col].replace(0, pd.NA)

        if method == "median":
            fill_val = df[col].median()
        elif method == "mean":
            fill_val = df[col].mean()
        else:
            raise ValueError("method must be 'median' or 'mean'")
                
    df[col] = df[col].fillna(fill_val)

    df['scraped_at'] = pd.to_datetime(df['scraped_at'], errors='coerce')
    df['hour'] = df['scraped_at'].dt.hour
    df.loc[
        (df['max_uv_index'] == 0) & (df['hour'].between(6, 18)),
        'max_uv_index'
    ] = pd.NA
    df['max_uv_index'] = df['max_uv_index'].fillna(df['max_uv_index'].median())
    
    
    return df

def fill_missing_value_for_strings(df: pd.DataFrame)-> pd.DataFrame:
    cols_null_invalid = {
            'city',
            'task_id',
            'wind_direction',
            'weather_condition'  
        }
    
    for col in cols_null_invalid:
        df[col] = df[col].replace(["Null", "", "None"], pd.NA)
        df[col] = df[col].fillna("Unknown")
    return df


def standardize_strings(df: pd.DataFrame):
    # city.title(), weather_condition.lower(), etc.
    df['city'] = df['city'].str.strip().str.title()
    df['weather_condition'] = df['weather_condition'].str.strip().str.lower()
    df['wind_direction'] = df['wind_direction'].str.strip().str.upper()
    pass


def normalize_datetime(df):
    # remove microseconds, ensure timezone consistency
    # 1. Ensure proper datetime format
    df['scraped_at'] = pd.to_datetime(df['scraped_at'], errors='coerce')

    # 2. Remove microseconds (clean timestamps)
    df['scraped_at'] = df['scraped_at'].dt.floor('s')

    # 3. Ensure timezone consistency (convert to UTC if timezone exists)
    if df['scraped_at'].dt.tz is not None:
        df['scraped_at'] = df['scraped_at'].dt.tz_convert('UTC')

    # 4. Create useful analysis columns
    df['date'] = df['scraped_at'].dt.date
    df['hour'] = df['scraped_at'].dt.hour
    df['day_of_week'] = df['scraped_at'].dt.day_name()
    pass