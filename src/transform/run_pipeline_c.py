#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os

from .transform_data import (
    RAW_DIR,
    PROCESSED_DIR,
    ensure_dirs,
    transform_apps,
    transform_reviews,
)
from .compute_app_kpis import compute_app_kpis
from .compute_daily_metrics import compute_daily_metrics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the analytics pipeline for Part C scenarios."
    )
    parser.add_argument(
        "--apps",
        default="apps_metadata_raw.json",
        help="Raw apps file name in data/raw (JSON or CSV).",
    )
    parser.add_argument(
        "--reviews",
        default="user_reviews_raw.jsonl",
        help="Raw reviews file name in data/raw (JSONL or CSV).",
    )
    args = parser.parse_args()

    ensure_dirs()

    apps_in = os.path.join(RAW_DIR, args.apps)
    reviews_in = os.path.join(RAW_DIR, args.reviews)

    if not os.path.exists(apps_in):
        raise FileNotFoundError(f"Raw apps file not found in data/raw: {args.apps}")
    if not os.path.exists(reviews_in):
        raise FileNotFoundError(f"Raw reviews file not found in data/raw: {args.reviews}")

    apps_out = os.path.join(PROCESSED_DIR, "apps_metadata_processed.json")
    reviews_out = os.path.join(PROCESSED_DIR, "user_reviews_processed.jsonl")

    transform_apps(apps_in, apps_out)
    transform_reviews(reviews_in, reviews_out)

    app_kpis_out = os.path.join(PROCESSED_DIR, "app_kpis.csv")
    daily_metrics_out = os.path.join(PROCESSED_DIR, "daily_metrics.csv")

    compute_app_kpis(reviews_out, app_kpis_out)
    compute_daily_metrics(reviews_out, daily_metrics_out)


if __name__ == "__main__":
    main()


