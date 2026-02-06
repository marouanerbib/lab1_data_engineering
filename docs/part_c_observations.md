# Part C – Pipeline Changes and Stress Testing

This document summarizes how the current pipeline behaves for the Part C scenarios and where changes were made.

## 1. New Reviews Batch (`note_taking_ai_reviews_batch2.csv`)

**How to run**

```bash
cd /home/horhoro/projects/lab1_data_engineering
python src/transform/run_pipeline_c.py --reviews note_taking_ai_reviews_batch2.csv
```

**Behavior**

- The transform layer now accepts CSV as a raw reviews source and normalizes it into the same internal schema used for JSONL.
- Running `run_pipeline_c.py` always performs a full refresh: processed reviews, app KPIs, and daily metrics are recomputed from the chosen raw files.
- Duplicate reviews are not deduplicated; they are counted as independent events in KPIs and daily metrics (this is acceptable for a batch-oriented full rebuild, but should be called out in documentation).
- Reviews referencing unknown `appId` values still flow through and appear as separate apps in `app_kpis.csv`; the pipeline does not enforce referential integrity at this stage.

## 2. Schema Drift in Reviews (`note_taking_ai_reviews_schema_drift.csv`)

**How to run**

```bash
cd /home/horhoro/projects/lab1_data_engineering
python src/transform/run_pipeline_c.py --reviews note_taking_ai_reviews_schema_drift.csv
```

**Code changes**

- `transform_data.transform_reviews` was refactored to route through helpers:
  - `_iter_reviews_jsonl` for the original JSONL file.
  - `_iter_reviews_csv` for CSV sources, with column mapping implemented in `_normalize_review_row`.
- `_normalize_review_row` uses a small name-mapping layer so that common schema drift variants (e.g. `review_id` vs `reviewId`, `rating` vs `score`) still map into the canonical fields.

**Observations**

- Parts of the original pipeline that relied on exact column names are now isolated inside `_normalize_review_row`.
- If a column cannot be mapped, the corresponding field becomes `None`, which then flows into the existing normalization logic (e.g. `safe_int` and timestamp parsing) rather than crashing.
- Failures are mostly explicit: missing timestamps lead to `at_iso=None` and those records still exist but may not contribute to time-based aggregations.
- Changes are localized to `transform_data.py`; downstream analytics and dashboard code remain unchanged.

## 3. Dirty and Inconsistent Data Records (`note_taking_ai_reviews_dirty.csv`)

**How to run**

```bash
cd /home/horhoro/projects/lab1_data_engineering
python src/transform/run_pipeline_c.py --reviews note_taking_ai_reviews_dirty.csv
```

**Behavior**

- Invalid ratings are passed through `safe_int`; non-numeric values become `None` and are excluded from averages and low-rating percentages.
- Malformed timestamps fall back to `parse_human_datetime`; if parsing still fails, `at_iso` remains `None` and those rows are effectively dropped from date-based aggregates.
- Problematic records are generally transformed into partially-null records rather than being dropped entirely; some data quality issues therefore propagate into aggregates as missing values rather than raising hard failures.

## 4. Updated Applications Metadata (`note_taking_ai_apps_updated.csv`)

**How to run**

```bash
cd /home/horhoro/projects/lab1_data_engineering
python src/transform/run_pipeline_c.py --apps note_taking_ai_apps_updated.csv
```

**Behavior**

- `transform_apps` now supports both JSON and CSV inputs; it reads CSV rows and applies the same normalization logic (installs, dates, categories) where fields are available.
- Duplicate application identifiers are not deduplicated at the transform stage; any code that builds `appId -> title` mappings (e.g. the dashboard) will effectively let the last occurrence win.
- Since the core aggregations (`compute_app_kpis.py`, `compute_daily_metrics.py`) operate only on review records keyed by `appId`, they do not break when app metadata contains duplicates or missing values; they simply reflect whatever `appId` values exist in the reviews.
- Joins in the dashboard layer (mapping `appId` to title) are tolerant of missing metadata: when an `appId` is not present, the dashboard falls back to displaying the raw `appId`.

## 5. New Business Logic – Inconsistent Sentiment

**Question**

> “We want to identify applications where the sentiment in review text contradicts the numeric rating.”

**Implementation**

- A new script `src/transform/flag_inconsistent_sentiment.py` reads `user_reviews_processed.jsonl` and writes:
  - `data/processed/inconsistent_sentiment_reviews.csv`
- It applies a simple heuristic:
  - Tag text as negative if it contains typical negative terms (e.g. “bad”, “terrible”, “scam”, “doesn't work”, “waste”).
  - Tag text as positive if it contains typical positive terms (e.g. “great”, “excellent”, “love”, “amazing”).
  - Flag a review as “inconsistent” when:
    - Negative text with a numeric score ≥ 4, or
    - Positive text with a numeric score ≤ 2.

**How to run**

```bash
cd /home/horhoro/projects/lab1_data_engineering
python src/transform/flag_inconsistent_sentiment.py
```

**Pipeline impact**

- The new logic sits in a separate transform script that depends only on the processed reviews file, keeping it clearly in the serving/analytics layer rather than in raw ingestion.
- No changes were required to raw ingestion or core aggregations; the new output is an additional dataset that downstream analysts can consume.
- The sentiment heuristic is easy to evolve (e.g. plug in a proper NLP model) without touching the rest of the pipeline.
- The structure maintains a clear separation between:
  - **Data preparation** (raw → processed normalized reviews/apps).
  - **Analytics / serving** (KPIs, daily metrics, and the new inconsistent-sentiment report).


