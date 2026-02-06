#!/usr/bin/env python3
"""Transform raw Play Store data into normalized processed files.

Outputs written to data/processed/:
 - apps_metadata_processed.json  (array of app objects)
 - user_reviews_processed.jsonl  (JSONL, one review per line)

Notes (informal):
 - Keep `userName` and `userImage` as requested.
 - Parse timestamps to ISO and epoch; normalize numeric fields.
 - Strip HTML from `descriptionHTML` into `description_text` using a simple regex.
"""
from __future__ import annotations

import csv
import json
import os
import re
import html
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Mapping


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW_DIR = os.path.join(ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(ROOT, "data", "processed")


def ensure_dirs() -> None:
    os.makedirs(PROCESSED_DIR, exist_ok=True)


def strip_html(text: str) -> str:
    if text is None:
        return ""
    # Unescape HTML entities
    t = html.unescape(text)
    # Remove tags
    t = re.sub(r"<[^>]+>", "", t)
    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


def parse_epoch_int(ts: Any) -> int | None:
    try:
        if ts is None:
            return None
        return int(ts)
    except Exception:
        return None


def epoch_to_iso(e: int | None) -> str | None:
    if not e:
        return None
    try:
        return datetime.fromtimestamp(int(e), tz=timezone.utc).isoformat()
    except Exception:
        return None


def parse_human_datetime(s: str) -> str | None:
    if not s:
        return None
    # Try common formats seen in data: 'Jan 5, 2026' or '2025-11-08 13:54:14'
    for fmt in ("%Y-%m-%d %H:%M:%S", "%b %d, %Y", "%B %d, %Y"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except Exception:
            continue
    # Fallback: return original trimmed
    return s.strip()


def normalize_installs(app: Dict[str, Any]) -> Dict[str, Any]:
    # prefer numeric fields when available
    min_installs = app.get("minInstalls")
    real_installs = app.get("realInstalls")
    installs_str = app.get("installs")
    if not min_installs and isinstance(installs_str, str):
        m = re.search(r"([0-9,]+)"+r"\+?", installs_str.replace(',', ''))
        if m:
            try:
                min_installs = int(re.sub(r"[^0-9]", "", installs_str))
            except Exception:
                min_installs = None
    app["minInstalls"] = int(min_installs) if min_installs is not None else None
    app["realInstalls"] = int(real_installs) if real_installs is not None else None
    return app


def transform_apps(in_path: str, out_path: str) -> None:
    print(f"Reading apps from {in_path}")
    with open(in_path, "r", encoding="utf-8") as f:
        if in_path.lower().endswith(".json"):
            apps = json.load(f)
        else:
            reader = csv.DictReader(f)
            apps = list(reader)

    processed = []
    for a in apps:
        app = dict(a)
        # description text (strip HTML)
        app["description_text"] = strip_html(app.get("descriptionHTML") or app.get("description") or "")

        # normalize installs
        app = normalize_installs(app)

        # epoch -> iso
        app["updated_iso"] = epoch_to_iso(parse_epoch_int(app.get("updated")))

        # human dates
        app["released_iso"] = parse_human_datetime(app.get("released"))
        app["lastUpdatedOn_iso"] = parse_human_datetime(app.get("lastUpdatedOn"))

        # categories flatten
        cats = app.get("categories") or []
        app["category_ids"] = [c.get("id") for c in cats if isinstance(c, dict) and c.get("id")]
        app["category_names"] = [c.get("name") for c in cats if isinstance(c, dict) and c.get("name")]

        # keep only needed large lists as-is (apps may have many screenshots)
        # leave `screenshots`, `icon`, `headerImage` intact

        processed.append(app)

    print(f"Writing {len(processed)} apps to {out_path}")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)


def safe_int(v: Any) -> int | None:
    try:
        if v is None:
            return None
        return int(v)
    except Exception:
        return None


def _iter_reviews_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                try:
                    start = line.find("{")
                    end = line.rfind("}")
                    obj = json.loads(line[start : end + 1])
                except Exception:
                    continue
            yield obj


def _get_first(mapping: Mapping[str, Any], candidates: list[str]) -> Any:
    lower_map = {k.lower(): v for k, v in mapping.items()}
    for name in candidates:
        v = lower_map.get(name.lower())
        if v is not None:
            return v
    return None


def _normalize_review_row(row: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "reviewId": _get_first(row, ["reviewId", "review_id", "id"]),
        "userName": _get_first(row, ["userName", "user_name", "author", "author_name"]),
        "userImage": _get_first(row, ["userImage", "user_image", "avatar"]),
        "content": _get_first(row, ["content", "review_text", "text", "body"]),
        "score": _get_first(row, ["score", "rating", "stars"]),
        "thumbsUpCount": _get_first(row, ["thumbsUpCount", "likes", "helpful_count"]),
        "reviewCreatedVersion": _get_first(row, ["reviewCreatedVersion", "review_version"]),
        "at": _get_first(row, ["at", "timestamp", "created_at"]),
        "replyContent": _get_first(row, ["replyContent", "reply_text"]),
        "repliedAt": _get_first(row, ["repliedAt", "reply_timestamp"]),
        "appVersion": _get_first(row, ["appVersion", "app_version"]),
        "appId": _get_first(row, ["appId", "app_id"]),
    }


def _iter_reviews_csv(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            yield _normalize_review_row(row)


def _iter_reviews(in_path: str) -> Iterable[Dict[str, Any]]:
    if in_path.lower().endswith(".csv"):
        yield from _iter_reviews_csv(in_path)
    else:
        yield from _iter_reviews_jsonl(in_path)


def transform_reviews(in_path: str, out_path: str, max_lines: int | None = None) -> None:
    print(f"Reading reviews from {in_path} and writing processed JSONL to {out_path}")
    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Raw reviews file not found: {in_path}")

    count = 0
    tmp_out = out_path + ".tmp"
    with open(tmp_out, "w", encoding="utf-8") as fout:
        for obj in _iter_reviews(in_path):
            r = dict(obj)

            at_raw = r.get("at")
            at_iso = None
            at_epoch = None
            if isinstance(at_raw, str) and at_raw:
                try:
                    dt = datetime.strptime(at_raw, "%Y-%m-%d %H:%M:%S")
                    dt = dt.replace(tzinfo=timezone.utc)
                    at_iso = dt.isoformat()
                    at_epoch = int(dt.timestamp())
                except Exception:
                    at_iso = parse_human_datetime(at_raw)

            r["at_iso"] = at_iso
            r["at_epoch"] = at_epoch

            r["score"] = safe_int(r.get("score"))
            r["thumbsUpCount"] = safe_int(r.get("thumbsUpCount"))

            fout.write(json.dumps(r, ensure_ascii=False) + "\n")
            count += 1
            if max_lines and count >= max_lines:
                break

    os.replace(tmp_out, out_path)
    print(f"Wrote {count} reviews")


def main() -> None:
    ensure_dirs()

    apps_in = os.path.join(RAW_DIR, "apps_metadata_raw.json")
    apps_out = os.path.join(PROCESSED_DIR, "apps_metadata_processed.json")

    reviews_in = os.path.join(RAW_DIR, "user_reviews_raw.jsonl")
    reviews_out = os.path.join(PROCESSED_DIR, "user_reviews_processed.jsonl")

    transform_apps(apps_in, apps_out)
    transform_reviews(reviews_in, reviews_out)


if __name__ == "__main__":
    main()
