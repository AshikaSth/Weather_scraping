# analytics/clean.py

import logging
import pandas as pd
from app import db
from app.models.weather import WeatherRecord

# ── Logger setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ── Public entry points ──────────────────────────────────────────────────────

def load_raw_data() -> pd.DataFrame:
    """Load raw weather records from the database into a DataFrame."""
    logger.info("Loading raw weather data from database...")
    records = WeatherRecord.query.all()
    df = pd.DataFrame([{
        'id':                r.id,
        'city':              r.city,
        'scraped_at':        r.scraped_at,
        'task_id':           r.task_id,
        'temperature':       r.temperature,
        'real_feel':         r.real_feel,
        'weather_condition': r.weather_condition,
        'humidity':          r.humidity,
        'wind_speed':        r.wind_speed,
        'wind_direction':    r.wind_direction,
        'visibility':        r.visibility,
        'max_uv_index':      r.max_uv_index,
        'dew_point':         r.dew_point,
        'pressure':          r.pressure,
        'cloud_cover':       r.cloud_cover,
        'cloud_ceiling':     r.cloud_ceiling,
        'precipitation':     r.precipitation,
        'rain':              r.rain,
    } for r in records])
    logger.info("Loaded %d raw records.", len(df))
    return df


def clean_data(df: pd.DataFrame = None, method: str = "median") -> pd.DataFrame:
    """
    Run the full cleaning pipeline on a weather DataFrame.

    Parameters
    ----------
    df     : Raw DataFrame. If None, data is loaded from the database.
    method : Strategy for filling missing numeric values ('median' or 'mean').
    """
    if df is None:
        df = load_raw_data()

    logger.info("Starting cleaning pipeline on %d rows.", len(df))

    df = remove_duplicates(df)
    df = coerce_numeric_columns(df)
    df = normalize_datetime(df)          # must run before UV-index logic
    df = handle_outliers(df)
    df = fill_missing_numeric_values(df, method=method)
    df = fill_missing_string_values(df)
    df = standardize_strings(df)

    logger.info("Cleaning pipeline complete. %d rows remaining.", len(df))
    return df


# ── Pipeline steps ───────────────────────────────────────────────────────────

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows that share the same task_id + city, keeping the first occurrence."""
    before = len(df)
    df = df.drop_duplicates(subset=['task_id', 'city'], keep='first')
    df = df.reset_index(drop=True)
    removed = before - len(df)
    if removed:
        logger.warning("Removed %d duplicate row(s) (task_id + city).", removed)
    else:
        logger.info("No duplicates found.")
    return df


def coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Coerce all numeric weather columns to proper numeric types so that
    downstream comparisons never raise TypeError on mixed-type data.
    """
    numeric_cols = [
        'temperature', 'real_feel', 'humidity', 'wind_speed',
        'visibility', 'max_uv_index', 'dew_point', 'pressure',
        'cloud_cover', 'cloud_ceiling', 'precipitation', 'rain',
    ]
    for col in numeric_cols:
        before_nulls = df[col].isna().sum()
        df[col] = pd.to_numeric(df[col], errors='coerce')
        new_nulls = df[col].isna().sum() - before_nulls
        if new_nulls > 0:
            logger.warning(
                "Column '%s': %d value(s) could not be coerced to numeric and were set to NA.",
                col, new_nulls,
            )
    logger.info("Numeric coercion complete.")
    return df


def normalize_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the scraped_at column:
      - Parse to datetime
      - Strip microseconds
      - Convert to UTC if timezone-aware
      - Derive analysis columns: date, hour, day_of_week
    """
    df['scraped_at'] = pd.to_datetime(df['scraped_at'], errors='coerce')
    invalid_dates = df['scraped_at'].isna().sum()
    if invalid_dates:
        logger.warning("%d row(s) have an unparseable scraped_at value.", invalid_dates)

    df['scraped_at'] = df['scraped_at'].dt.floor('s')

    if df['scraped_at'].dt.tz is not None:
        df['scraped_at'] = df['scraped_at'].dt.tz_convert('UTC')
        logger.info("scraped_at converted to UTC.")

    df['date']        = df['scraped_at'].dt.date
    df['hour']        = df['scraped_at'].dt.hour
    df['day_of_week'] = df['scraped_at'].dt.day_name()

    logger.info("Datetime normalization complete.")
    return df


def handle_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Replace out-of-domain values with NA using meteorological bounds."""
    rules = {
        'temperature':  (-50,  60),
        'real_feel':    (-50,  60),
        'humidity':     (  0, 100),
        'wind_speed':   (  0, 150),
        'visibility':   (  0,  50),
        'max_uv_index': (  0,  15),
        'dew_point':    (-50,  40),
        'pressure':     (870, 1085),
        'cloud_cover':  (  0, 100),
        'cloud_ceiling':(  0, 20000),
        'precipitation':(  0, 500),
        'rain':         (  0, 500),
    }

    for col, (min_val, max_val) in rules.items():
        mask = (df[col] < min_val) | (df[col] > max_val)
        outlier_count = mask.sum()
        if outlier_count:
            logger.warning(
                "Column '%s': %d outlier(s) outside [%s, %s] set to NA.",
                col, outlier_count, min_val, max_val,
            )
            df.loc[mask, col] = pd.NA

    logger.info("Outlier handling complete.")
    return df


def fill_missing_numeric_values(df: pd.DataFrame, method: str = "median") -> pd.DataFrame:
    """
    Fill missing / zero-invalid numeric values using per-city median or mean.

    Zero is treated as invalid for meteorological columns where 0 is physically
    implausible (e.g. pressure, visibility). precipitation and rain are excluded
    because 0 mm is a valid observation.

    UV index is only filled for daytime hours (6–18) because a night-time
    reading of 0 is legitimate.
    """
    if method not in ("median", "mean"):
        raise ValueError("method must be 'median' or 'mean'")

    # Columns where 0 is an invalid sentinel
    zero_invalid_cols = [
        'temperature', 'real_feel', 'humidity',
        'visibility', 'dew_point', 'pressure',
        'cloud_cover', 'cloud_ceiling',
    ]

    for col in zero_invalid_cols:
        zero_count = (df[col] == 0).sum()
        if zero_count:
            logger.info("Column '%s': replacing %d zero(s) with NA before fill.", col, zero_count)
        df[col] = df[col].replace(0, pd.NA)

        # Per-city fill for better accuracy
        fill_series = df.groupby('city')[col].transform(method)
        # Fall back to global statistic for cities with no valid data at all
        global_fill = getattr(df[col], method)()
        filled_count = df[col].isna().sum()
        df[col] = df[col].fillna(fill_series).fillna(global_fill)
        logger.info(
            "Column '%s': filled %d missing value(s) using per-city %s (global fallback: %.4f).",
            col, filled_count, method, global_fill,
        )

    # UV index: only flag daytime zeros as missing
    daytime_zero_mask = (df['max_uv_index'] == 0) & (df['hour'].between(6, 18))
    daytime_zero_count = daytime_zero_mask.sum()
    if daytime_zero_count:
        logger.info(
            "max_uv_index: replacing %d daytime zero(s) with NA.", daytime_zero_count,
        )
        df.loc[daytime_zero_mask, 'max_uv_index'] = pd.NA

    uv_fill_series  = df.groupby('city')['max_uv_index'].transform(method)
    uv_global_fill  = getattr(df['max_uv_index'], method)()
    uv_filled_count = df['max_uv_index'].isna().sum()
    df['max_uv_index'] = df['max_uv_index'].fillna(uv_fill_series).fillna(uv_global_fill)
    logger.info(
        "max_uv_index: filled %d missing value(s) (global fallback: %.4f).",
        uv_filled_count, uv_global_fill,
    )

    # precipitation / rain — fill remaining NAs with 0 (no rain is valid)
    for col in ('precipitation', 'rain'):
        na_count = df[col].isna().sum()
        if na_count:
            logger.info("Column '%s': filling %d NA(s) with 0.", col, na_count)
            df[col] = df[col].fillna(0)

    logger.info("Missing numeric value fill complete.")
    return df


def fill_missing_string_values(df: pd.DataFrame) -> pd.DataFrame:
    """Replace placeholder / null-like strings with 'Unknown'."""
    string_cols = ['city', 'task_id', 'wind_direction', 'weather_condition']
    placeholders = ["Null", "null", "", "None", "none", "N/A", "n/a"]

    for col in string_cols:
        df[col] = df[col].replace(placeholders, pd.NA)
        missing_count = df[col].isna().sum()
        if missing_count:
            logger.warning(
                "Column '%s': %d missing/placeholder value(s) replaced with 'Unknown'.",
                col, missing_count,
            )
        df[col] = df[col].fillna("Unknown")

    logger.info("String placeholder fill complete.")
    return df


def standardize_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize casing and whitespace for string columns."""
    df['city']              = df['city'].str.strip().str.title()
    df['weather_condition'] = df['weather_condition'].str.strip().str.lower()
    df['wind_direction']    = df['wind_direction'].str.strip().str.upper()
    logger.info("String standardization complete.")
    return df