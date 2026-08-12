"""
app/analytics/insights.py
--------------------------
Generates AI-powered pollution insights for Kathmandu visibility data.
Keeps insight logic completely separate from charting and routing.
"""

import textwrap
import pandas as pd
from anthropic import Anthropic

POOR_VISIBILITY_KM = 5.0


def generate_insight(df: pd.DataFrame) -> str:
    """
    Send summary stats to Claude and return a concise pollution insight.
    Falls back to a rule-based summary if the API call fails.
    """
    stats = {
        "mean_visibility_km": round(df["visibility"].mean(), 2),
        "min_visibility_km":  round(df["visibility"].min(), 2),
        "max_visibility_km":  round(df["visibility"].max(), 2),
        "pct_below_5km":      round(
            (df["visibility"] < POOR_VISIBILITY_KM).mean() * 100, 1
        ),
        "worst_time": str(df.loc[df["visibility"].idxmin(), "scraped_at"]),
        "best_time":  str(df.loc[df["visibility"].idxmax(), "scraped_at"]),
        "total_records": len(df),
    }

    prompt = f"""
You are an environmental data analyst specializing in South Asian air quality.
Below are visibility statistics for Kathmandu, Nepal.
Visibility is used as a proxy for air pollution (smog, dust, vehicle emissions).

Statistics:
{stats}

Write a concise insight (3–4 sentences) that:
1. States the overall visibility health of KTM based on these numbers.
2. Highlights the worst period and what typically causes low visibility in KTM at that time.
3. Ends with one actionable recommendation for residents.

Be specific, data-driven, and avoid generic statements.
"""

    try:
        client = Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    except Exception as e:
        # Graceful fallback — rule-based summary if API is unavailable
        return _fallback_insight(df, stats, error=str(e))


def _fallback_insight(df: pd.DataFrame, stats: dict, error: str = "") -> str:
    """Rule-based insight used when the Anthropic API is unreachable."""
    mean_vis   = stats["mean_visibility_km"]
    pct_poor   = stats["pct_below_5km"]
    worst_time = stats["worst_time"]

    if mean_vis < 5:
        condition = f"poor, averaging {mean_vis} km — indicating frequent pollution conditions"
    elif mean_vis < 8:
        condition = f"moderate, averaging {mean_vis} km — suggesting occasional air quality issues"
    else:
        condition = f"generally good, averaging {mean_vis} km — indicating relatively cleaner air"

    parts = [
        f"Overall visibility is {condition}.",
        f"The worst reading ({stats['min_visibility_km']} km) occurred around {worst_time}, "
        f"likely due to dust, traffic emissions, or fog.",
        f"Approximately {pct_poor}% of readings fall below {POOR_VISIBILITY_KM} km.",
        "Residents should limit outdoor activities during low-visibility periods "
        "and wear masks in high-traffic areas.",
    ]
    note = f" (AI insight unavailable: {error})" if error else ""
    return " ".join(parts) + note


def print_insight(insight: str) -> None:
    """Pretty-print the insight to the terminal (useful for CLI runs)."""
    border = "─" * 70
    print(f"\n{border}")
    print("  🤖  AI Pollution Insight — Kathmandu Visibility")
    print(border)
    for line in textwrap.wrap(insight, width=68):
        print(f"  {line}")
    print(border + "\n")