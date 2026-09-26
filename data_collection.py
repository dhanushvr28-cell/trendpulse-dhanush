"""
TrendPulse - Task 1: Data Collection

Fetches live trending stories from the Hacker News public API and stores
the raw dataset as data/raw_trending_data.csv.

No API key is required.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"

DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_FILE = DATA_DIR / "raw_trending_data.csv"

NUMBER_OF_STORIES = 50
REQUEST_TIMEOUT = 15
MAX_WORKERS = 10


def get_json(session: requests.Session, url: str) -> Any:
    """GET JSON from a URL and raise a clear error if the request fails."""
    response = session.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_story(session: requests.Session, story_id: int, rank: int) -> dict[str, Any] | None:
    """Fetch one Hacker News story and normalize the fields we need."""
    item = get_json(session, ITEM_URL.format(item_id=story_id))

    if not item or item.get("type") != "story":
        return None

    return {
        "rank": rank,
        "id": item.get("id"),
        "title": item.get("title"),
        "author": item.get("by"),
        "score": item.get("score", 0),
        "comments": item.get("descendants", 0),
        "unix_time": item.get("time"),
        "url": item.get("url"),
        "type": item.get("type"),
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def collect_trending_stories(limit: int = NUMBER_OF_STORIES) -> pd.DataFrame:
    """Collect the current top Hacker News stories."""
    if limit <= 0:
        raise ValueError("limit must be greater than 0")

    headers = {
        "User-Agent": "TrendPulse/1.0 (educational data pipeline project)"
    }

    with requests.Session() as session:
        session.headers.update(headers)

        story_ids = get_json(session, TOP_STORIES_URL)
        if not isinstance(story_ids, list) or not story_ids:
            raise RuntimeError("The Hacker News API returned no top-story IDs.")

        selected_ids = story_ids[:limit]
        rows: list[dict[str, Any]] = []

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(fetch_story, session, story_id, rank): rank
                for rank, story_id in enumerate(selected_ids, start=1)
            }

            for future in as_completed(futures):
                rank = futures[future]
                try:
                    story = future.result()
                    if story is not None:
                        rows.append(story)
                except requests.RequestException as exc:
                    print(f"Warning: could not fetch story at rank {rank}: {exc}")

    if not rows:
        raise RuntimeError(
            "No stories were collected. Check your internet connection and try again."
        )

    return pd.DataFrame(rows).sort_values("rank").reset_index(drop=True)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Fetching the top {NUMBER_OF_STORIES} live Hacker News stories...")
    df = collect_trending_stories()

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Collected {len(df)} stories.")
    print(f"Saved raw data to: {OUTPUT_FILE}")
    print("\nPreview:")
    print(df[["rank", "title", "score", "comments"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
