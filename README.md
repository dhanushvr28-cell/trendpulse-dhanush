# TrendPulse

TrendPulse is a four-stage Python data pipeline that collects **live trending data**, cleans and enriches it, analyses the results, and creates a visual dashboard.

This implementation uses the **Hacker News public API**, so no API key is required.

## Project files

```text
trendpulse-project/
├── task1_data_collection.py
├── task2_data_processing.py
├── task3_analysis.py
├── task4_visualization.py
├── requirements.txt
├── data/
└── reports/
```

## Pipeline

### Task 1 — Data collection
`task1_data_collection.py`

- Fetches the current top Hacker News stories.
- Collects title, author, score, comments, URL, rank and timestamp.
- Saves the result to `data/raw_trending_data.csv`.

### Task 2 — Data processing
`task2_data_processing.py`

- Removes invalid and duplicate rows.
- Normalizes numeric fields and timestamps.
- Extracts source domains.
- Creates age, engagement and recency-aware trend-score features.
- Saves the result to `data/processed_trending_data.csv`.

### Task 3 — Analysis
`task3_analysis.py`

- Calculates summary statistics.
- Finds top trending stories, domains and authors.
- Measures score/comment correlation.
- Creates:
  - `reports/analysis_summary.json`
  - `reports/top_10_trending_stories.csv`
  - `reports/domain_summary.csv`

### Task 4 — Visualization
`task4_visualization.py`

Creates `reports/trendpulse_dashboard.png` containing:

- Top 10 stories by trend score
- Top source domains
- Score vs comments
- Age distribution of trending stories

## Setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### macOS/Linux

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Execute the scripts in order:

```bash
python task1_data_collection.py
python task2_data_processing.py
python task3_analysis.py
python task4_visualization.py
```

After Task 4, open:

```text
reports/trendpulse_dashboard.png
```

## Data source

Hacker News Firebase API:
`https://hacker-news.firebaseio.com/v0/`

The API is public and does not require authentication.
