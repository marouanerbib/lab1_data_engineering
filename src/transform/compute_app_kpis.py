#!/usr/bin/env python3
"""
Compute app-level KPIs from processed user reviews.

Input (already created by transform_data.py):
  - data/processed/user_reviews_processed.jsonl  (one JSON object per line)

Output (this script):
  - data/processed/app_kpis.csv

Each row in the CSV corresponds to one application (one appId) and contains:
  - appId
  - num_reviews              (total number of reviews for that app)
  - avg_rating               (average of `score` over reviews that have a rating)
  - low_rating_pct           (% of reviews with rating <= 2 among rated reviews)
  - first_review_date        (earliest review date in ISO format, based on `at_iso` then `at`)
  - last_review_date         (most recent review date in ISO format, based on `at_iso` then `at`)
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from typing import Dict, Optional


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROCESSED_DIR = os.path.join(ROOT, "data", "processed")


@dataclass
class AppAgg:
    app_id: str
    num_reviews: int = 0
    rated_reviews: int = 0
    score_sum: float = 0.0
    low_rated_reviews: int = 0
    first_date: Optional[str] = None
    last_date: Optional[str] = None

    def update(self, score: Optional[int], date_str: Optional[str]) -> None:
        # Count every review
        self.num_reviews += 1

        # Ratings-based stats
        if score is not None:
            self.rated_reviews += 1
            self.score_sum += score
            if score <= 2:
                self.low_rated_reviews += 1

        # Dates: keep min / max on comparable strings (ISO)
        if date_str:
            if self.first_date is None or date_str < self.first_date:
                self.first_date = date_str
            if self.last_date is None or date_str > self.last_date:
                self.last_date = date_str

    def to_row(self) -> Dict[str, object]:
        avg_rating: Optional[float]
        low_rating_pct: Optional[float]

        if self.rated_reviews > 0:
            avg_rating = self.score_sum / self.rated_reviews
            low_rating_pct = (self.low_rated_reviews / self.rated_reviews) * 100.0
        else:
            avg_rating = None
            low_rating_pct = None

        return {
            "appId": self.app_id,
            "num_reviews": self.num_reviews,
            "avg_rating": round(avg_rating, 3) if avg_rating is not None else "",
            "low_rating_pct": round(low_rating_pct, 3) if low_rating_pct is not None else "",
            "first_review_date": self.first_date or "",
            "last_review_date": self.last_date or "",
        }


def compute_app_kpis(
    reviews_path: str,
    out_csv_path: str,
) -> None:
    """Aggregate KPIs per appId from a processed reviews JSONL file."""
    print(f"Reading processed reviews from {reviews_path}")

    aggregates: Dict[str, AppAgg] = {}

    with open(reviews_path, "r", encoding="utf-8") as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except Exception:
                # Skip malformed lines
                continue

            app_id = obj.get("appId")
            if not app_id:
                continue

            score = obj.get("score")
            if isinstance(score, (int, float)):
                score_val: Optional[int] = int(score)
            else:
                score_val = None

            # Prefer normalized ISO timestamp from transform_data.py
            date_str = obj.get("at_iso") or obj.get("at")

            if app_id not in aggregates:
                aggregates[app_id] = AppAgg(app_id=app_id)

            aggregates[app_id].update(score=score_val, date_str=date_str)

    print(f"Computed aggregates for {len(aggregates)} apps")

    os.makedirs(os.path.dirname(out_csv_path), exist_ok=True)
    print(f"Writing app KPIs to {out_csv_path}")
    with open(out_csv_path, "w", encoding="utf-8", newline="") as fout:
        fieldnames = [
            "appId",
            "num_reviews",
            "avg_rating",
            "low_rating_pct",
            "first_review_date",
            "last_review_date",
        ]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for app_id in sorted(aggregates.keys()):
            writer.writerow(aggregates[app_id].to_row())


def main() -> None:
    reviews_in = os.path.join(PROCESSED_DIR, "user_reviews_processed.jsonl")
    out_csv = os.path.join(PROCESSED_DIR, "app_kpis.csv")

    if not os.path.exists(reviews_in):
        raise FileNotFoundError(
            f"Input file not found: {reviews_in}. "
            "Run transform_data.py first to generate processed reviews."
        )

    compute_app_kpis(reviews_in, out_csv)


if __name__ == "__main__":
    main()


