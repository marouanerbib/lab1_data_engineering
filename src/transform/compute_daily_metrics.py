#!/usr/bin/env python3
"""
Compute daily metrics from processed user reviews.

Input:
  - data/processed/user_reviews_processed.jsonl

Output:
  - data/processed/daily_metrics.csv

Each row in the CSV corresponds to one calendar date (UTC) and contains:
  - date               (YYYY-MM-DD)
  - daily_num_reviews  (number of reviews on that date)
  - daily_avg_rating   (average rating on that date, over reviews with a score)
"""

from __future__ import annotations

import csv
import json
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, Tuple


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROCESSED_DIR = os.path.join(ROOT, "data", "processed")


def _extract_date(obj: dict) -> str | None:
    """
    Extract YYYY-MM-DD date from a review object.
    Prefer `at_iso` (added in transform_data.py), fall back to `at`.
    """
    raw = obj.get("at_iso") or obj.get("at")
    if not raw:
        return None

    # If already ISO with date prefix, just slice the date part
    # e.g., "2025-12-24T21:16:45+00:00" -> "2025-12-24"
    try:
        if isinstance(raw, str) and len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
            return raw[:10]
    except Exception:
        pass

    # Fallback: try parsing "YYYY-MM-DD HH:MM:SS"
    if isinstance(raw, str):
        try:
            dt = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
            return dt.date().isoformat()
        except Exception:
            return None

    return None


def compute_daily_metrics(
    reviews_path: str,
    out_csv_path: str,
) -> None:
    print(f"Reading processed reviews from {reviews_path}")

    # date -> (count_reviews, count_rated, sum_scores)
    daily: Dict[str, Tuple[int, int, float]] = defaultdict(lambda: (0, 0, 0.0))

    with open(reviews_path, "r", encoding="utf-8") as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except Exception:
                continue

            date_str = _extract_date(obj)
            if not date_str:
                continue

            score = obj.get("score")
            rated = 0
            score_val = 0.0
            if isinstance(score, (int, float)):
                rated = 1
                score_val = float(score)

            count_reviews, count_rated, sum_scores = daily[date_str]
            count_reviews += 1
            count_rated += rated
            sum_scores += score_val
            daily[date_str] = (count_reviews, count_rated, sum_scores)

    print(f"Computed daily metrics for {len(daily)} dates")

    os.makedirs(os.path.dirname(out_csv_path), exist_ok=True)
    print(f"Writing daily metrics to {out_csv_path}")

    with open(out_csv_path, "w", encoding="utf-8", newline="") as fout:
        fieldnames = ["date", "daily_num_reviews", "daily_avg_rating"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for date_str in sorted(daily.keys()):
            count_reviews, count_rated, sum_scores = daily[date_str]
            if count_rated > 0:
                avg = round(sum_scores / count_rated, 3)
            else:
                avg = ""

            writer.writerow(
                {
                    "date": date_str,
                    "daily_num_reviews": count_reviews,
                    "daily_avg_rating": avg,
                }
            )


def main() -> None:
    reviews_in = os.path.join(PROCESSED_DIR, "user_reviews_processed.jsonl")
    out_csv = os.path.join(PROCESSED_DIR, "daily_metrics.csv")

    if not os.path.exists(reviews_in):
        raise FileNotFoundError(
            f"Input file not found: {reviews_in}. "
            "Run transform_data.py first to generate processed reviews."
        )

    compute_daily_metrics(reviews_in, out_csv)


if __name__ == "__main__":
    main()


