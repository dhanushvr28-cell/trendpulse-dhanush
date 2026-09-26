"""
TrendPulse - Task 3: Analysis

Analyses the processed trending dataset and creates:
- reports/analysis_summary.json
- reports/top_10_trending_stories.csv
- reports/domain_summary.csv
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "processed_trending_data.csv"
REPORTS_DIR = BASE_DIR / "reports"

SUMMARY_FILE = REPORTS_DIR / "analysis_summary.json"
TOP_STORIES_FILE = REPORTS_DIR / "top_10_trending_stories.csv"
DOMAIN_SUMMARY_FILE = REPORTS_DIR / "domain_summary.csv"


def safe_round(value: float, digits: int = 2) -> float:
    """Round a number while returning a normal Python float for JSON."""
    return round(float(value), digits)


def analyse(df: pd.DataFrame) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    """Create summary statistics and ranked tables."""
    if df.empty:
        raise ValueError("Processed dataset is empty.")

    top_10 = (
        df.sort_values("trend_score", ascending=False)
        .head(10)[
            [
                "trend_position",
                "title",
                "domain",
                "author",
                "score",
                "comments",
                "age_hours",
                "trend_score",
                "url",
            ]
        ]
        .copy()
    )

    domain_summary = (
        df.groupby("domain", as_index=False)
        .agg(
            stories=("id", "count"),
            total_score=("score", "sum"),
            total_comments=("comments", "sum"),
            average_score=("score", "mean"),
            average_trend_score=("trend_score", "mean"),
        )
        .sort_values(["stories", "total_score"], ascending=False)
    )

    top_domains = (
        domain_summary.head(5)[["domain", "stories", "total_score"]]
        .to_dict(orient="records")
    )

    author_counts = df["author"].value_counts().head(5)
    top_authors = [
        {"author": str(author), "stories": int(count)}
        for author, count in author_counts.items()
    ]

    score_comment_corr = df["score"].corr(df["comments"])
    if pd.isna(score_comment_corr):
        score_comment_corr = 0.0

    newest = df.sort_values("published_at_utc").iloc[-1]
    oldest = df.sort_values("published_at_utc").iloc[0]
    top_story = top_10.iloc[0]

    summary: dict[str, Any] = {
        "stories_analysed": int(len(df)),
        "average_score": safe_round(df["score"].mean()),
        "median_score": safe_round(df["score"].median()),
        "average_comments": safe_round(df["comments"].mean()),
        "average_age_hours": safe_round(df["age_hours"].mean()),
        "score_comment_correlation": safe_round(score_comment_corr, 3),
        "top_story": {
            "title": str(top_story["title"]),
            "domain": str(top_story["domain"]),
            "score": int(top_story["score"]),
            "comments": int(top_story["comments"]),
            "trend_score": safe_round(top_story["trend_score"], 3),
        },
        "top_domains": top_domains,
        "top_authors": top_authors,
        "newest_story_title": str(newest["title"]),
        "oldest_story_title": str(oldest["title"]),
    }

    return summary, top_10, domain_summary


def main() -> None:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"{DATA_FILE} does not exist. Run task2_data_processing.py first."
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_FILE)
    summary, top_10, domain_summary = analyse(df)

    with SUMMARY_FILE.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    top_10.to_csv(TOP_STORIES_FILE, index=False)
    domain_summary.to_csv(DOMAIN_SUMMARY_FILE, index=False)

    print("TRENDPULSE ANALYSIS")
    print("=" * 60)
    print(f"Stories analysed      : {summary['stories_analysed']}")
    print(f"Average score         : {summary['average_score']}")
    print(f"Median score          : {summary['median_score']}")
    print(f"Average comments      : {summary['average_comments']}")
    print(f"Average age (hours)   : {summary['average_age_hours']}")
    print(
        f"Score/comment corr.   : {summary['score_comment_correlation']}"
    )
    print("\nTop trending story:")
    print(f"  {summary['top_story']['title']}")
    print(
        f"  Score={summary['top_story']['score']} | "
        f"Comments={summary['top_story']['comments']} | "
        f"Trend score={summary['top_story']['trend_score']}"
    )
    print("\nFiles created:")
    print(f"  {SUMMARY_FILE}")
    print(f"  {TOP_STORIES_FILE}")
    print(f"  {DOMAIN_SUMMARY_FILE}")


if __name__ == "__main__":
    main()
