#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict

from .transform_data import PROCESSED_DIR


NEGATIVE_TERMS = [
    "bad",
    "terrible",
    "horrible",
    "awful",
    "worst",
    "scam",
    "refund",
    "bug",
    "broken",
    "crash",
    "doesn't work",
    "doesnt work",
    "waste",
    "useless",
]

POSITIVE_TERMS = [
    "great",
    "excellent",
    "amazing",
    "love",
    "awesome",
    "fantastic",
    "perfect",
    "very good",
    "works well",
    "helpful",
]


def score_text(text: str) -> int:
    t = text.lower()
    neg = any(term in t for term in NEGATIVE_TERMS)
    pos = any(term in t for term in POSITIVE_TERMS)
    if neg and not pos:
        return -1
    if pos and not neg:
        return 1
    return 0


def is_contradictory(review: Dict[str, Any]) -> bool:
    score = review.get("score")
    content = review.get("content") or ""
    if score is None:
        return False
    text_score = score_text(content)
    if text_score < 0 and score >= 4:
        return True
    if text_score > 0 and score <= 2:
        return True
    return False


def main() -> None:
    reviews_in = os.path.join(PROCESSED_DIR, "user_reviews_processed.jsonl")
    out_path = os.path.join(PROCESSED_DIR, "inconsistent_sentiment_reviews.csv")

    if not os.path.exists(reviews_in):
        raise FileNotFoundError(
            f"Processed reviews not found at {reviews_in}. Run the transform pipeline first."
        )

    rows = []
    with open(reviews_in, "r", encoding="utf-8") as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if is_contradictory(obj):
                rows.append(
                    {
                        "reviewId": obj.get("reviewId"),
                        "appId": obj.get("appId"),
                        "score": obj.get("score"),
                        "content": obj.get("content"),
                    }
                )

    import csv

    with open(out_path, "w", encoding="utf-8", newline="") as fout:
        fieldnames = ["reviewId", "appId", "score", "content"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Wrote {len(rows)} inconsistent sentiment reviews to {out_path}")


if __name__ == "__main__":
    main()


