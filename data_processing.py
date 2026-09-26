"""
TrendPulse - Task 2: Data Processing

Loads data/raw_trending_data.csv, cleans it, creates useful features,
and stores the processed dataset as data/processed_trending_data.csv.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
INPUT_FILE = DATA_DIR / "raw_trending_data.csv"
OUTPUT_FILE = DATA_DIR / "processed_trending_data.csv"


def extract_domain(url: object) -> str:
    """Return a clean domain name from a URL."""
    if pd.isna(url) or not str(url).strip():
        return "news.ycombinator.com"

    try:
        domain = urlparse(str(url)).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain or "news.ycombinator.com"
    except ValueError:
        return "unknown"


def clean_and_engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the raw data and add analysis-friendly features."""
    required = {
        "rank",
        "id",
        "title",
        "author",
        "score",
        "comments",
        "unix_time",
        "url",
    }

    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    cleaned = df.copy()

    # Remove unusable/duplicate rows.
    cleaned = cleaned.dropna(subset=["id", "title"])
    cleaned["title"] = cleaned["title"].astype(str).str.strip()
    cleaned = cleaned[cleaned["title"].ne("")]
    cleaned = cleaned.drop_duplicates(subset=["id"], keep="first")
    cleaned = cleaned.drop_duplicates(subset=["title"], keep="first")

    # Normalize numeric columns.
    for column in ["rank", "id", "score", "comments", "unix_time"]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned = cleaned.dropna(subset=["rank", "id", "unix_time"])
    cleaned["score"] = cleaned["score"].fillna(0).clip(lower=0)
    cleaned["comments"] = cleaned["comments"].fillna(0).clip(lower=0)

    # Convert timestamps.
    cleaned["published_at_utc"] = pd.to_datetime(
        cleaned["unix_time"], unit="s", utc=True, errors="coerce"
    )
    cleaned = cleaned.dropna(subset=["published_at_utc"])

    now = pd.Timestamp.now(tz="UTC")
    cleaned["age_hours"] = (
        (now - cleaned["published_at_utc"]).dt.total_seconds() / 3600
    ).clip(lower=0)

    # Text and source features.
    cleaned["author"] = cleaned["author"].fillna("unknown").astype(str)
    cleaned["domain"] = cleaned["url"].apply(extract_domain)
    cleaned["title_length"] = cleaned["title"].str.len()
    cleaned["title_word_count"] = cleaned["title"].str.split().str.len()

    # Engagement combines votes and discussion.
    cleaned["engagement"] = cleaned["score"] + (cleaned["comments"] * 2)

    # Recency-aware trend score: high engagement + newer stories rank higher.
    cleaned["trend_score"] = (
        cleaned["engagement"] / np.power(cleaned["age_hours"] + 2, 1.25)
    ).round(3)

    cleaned = cleaned.sort_values(
        ["trend_score", "score", "comments"], ascending=False
    ).reset_index(drop=True)

    cleaned["trend_position"] = range(1, len(cleaned) + 1)

    return cleaned


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"{INPUT_FILE} does not exist. Run task1_data_collection.py first."
        )

    df = pd.read_csv(INPUT_FILE)
    cleaned = clean_and_engineer_features(df)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(OUTPUT_FILE, index=False)

    print(f"Input rows: {len(df)}")
    print(f"Clean rows: {len(cleaned)}")
    print(f"Saved processed data to: {OUTPUT_FILE}")
    print("\nTop processed stories:")
    print(
        cleaned[
            ["trend_position", "title", "domain", "score", "comments", "trend_score"]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
