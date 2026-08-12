"""
app/analytics/analysis.py
--------------------------
Visibility Over Time — Pollution Proxy

Produces:
  - Chart.js data for interactive visualization in analysis.html
  - Shaded danger zone (< 5 km = poor air quality)

Insight generation has been moved to app/analytics/insights.py
"""

import pandas as pd
import json
from app.analytics.clean import clean_data
from scipy import stats
# ── Constants ─────────────────────────────────────────────────────────────────
POOR_VISIBILITY_KM = 5.0
DANGER_COLOR       = "#FF6B6B"
LINE_COLOR         = "#4A90D9"
ROLLING_COLOR      = "#1A3A5C"


# ── 1. Load data ──────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    return clean_data()

# visibility over time
# ── 2. Prepare visibility series ──────────────────────────────────────────────
def prepare_visibility(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["scraped_at"] = pd.to_datetime(df["scraped_at"], errors="coerce")
    df = df.dropna(subset=["scraped_at", "visibility"])
    df = df.sort_values("scraped_at").reset_index(drop=True)

    # Rolling 6-hour average (smooths sensor noise)
    df["visibility_rolling"] = (
        df["visibility"]
        .rolling(window=6, min_periods=1, center=True)
        .mean()
    )
    return df


# ── 3. Generate Chart.js data ─────────────────────────────────────────────────
def get_chart_data():
    """Export visibility data formatted for Chart.js"""
    df = prepare_visibility(load_data())
    
    # Find worst and best visibility points
    worst_idx = df["visibility_rolling"].idxmin()
    best_idx = df["visibility_rolling"].idxmax()
    
    return {
        "labels": df["scraped_at"].dt.strftime("%b %d %H:%M").tolist(),
        "datasets": [
            {
                "label": "Visibility (raw)",
                "data": df["visibility"].round(1).tolist(),
                "borderColor": LINE_COLOR,
                "backgroundColor": f"rgba(74, 144, 217, 0.1)",
                "borderWidth": 1,
                "pointRadius": 0,
                "tension": 0.3,
                "fill": False,
                "order": 2,
            },
            {
                "label": "6-hour rolling avg",
                "data": df["visibility_rolling"].round(1).tolist(),
                "borderColor": ROLLING_COLOR,
                "backgroundColor": f"rgba(26, 58, 92, 0.15)",
                "borderWidth": 2.5,
                "pointRadius": 0,
                "tension": 0.4,
                "fill": True,
                "order": 1,
            }
        ],
        "poorVisibilityThreshold": POOR_VISIBILITY_KM,
        "worstPoint": {
            "index": int(worst_idx),
            "value": round(df.loc[worst_idx, "visibility_rolling"], 1),
            "date": df.loc[worst_idx, "scraped_at"].strftime("%b %d %H:%M"),
        },
        "bestPoint": {
            "index": int(best_idx),
            "value": round(df.loc[best_idx, "visibility_rolling"], 1),
            "date": df.loc[best_idx, "scraped_at"].strftime("%b %d %H:%M"),
        }
    }


def get_humidity_visibility_data():
    """Export humidity vs visibility data for scatter plot with correlation analysis"""
    df = prepare_visibility(load_data())
    df = df.dropna(subset=["humidity", "visibility"])
    
    if len(df) == 0:
        return{
            "points": [],
            "correlation": 0,
            "trendLine": {"x": [], "y": []},
            "dataCount": 0,
            "message": "No data available"
        }
    
    #get data points
    humidity_vals = df["humidity"].values
    visibility_vals = df["visibility"].values

    #calculate pearson correlation
    correlation, p_value = stats.pearsonr(
        humidity_vals,
        visibility_vals
    )

    # Calculate linear regression for trend line
    slope, intercept, r_value, _, _ = stats.linregress(
        humidity_vals,
        visibility_vals
    )

    # Generate trend-line points
    x_min = humidity_vals.min()
    x_max = humidity_vals.max()

    trend_x = [float(x_min), float(x_max)]
    trend_y = [
        float(slope * x_min + intercept),
        float(slope * x_max + intercept)
    ]

    # Prepare scatter plot points
    points = [
        {
            "x": round(float(humidity), 2),
            "y": round(float(visibility), 2)
        }
        for humidity, visibility
        in zip(humidity_vals, visibility_vals)
    ]

    return {
        "points": points,
        "correlation": round(float(correlation), 3),
        "pValue": round(float(p_value), 5),
        "trendLine": {
            "x": [round(x, 2) for x in trend_x],
            "y": [round(y, 2) for y in trend_y]
        },
        "dataCount": len(points),
        "message": "Data available"
    }