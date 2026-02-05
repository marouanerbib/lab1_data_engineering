#!/usr/bin/env python3
"""
Create an interactive dashboard from processed analytics data.

This dashboard helps answer:
- Which applications perform best/worst according to user reviews?
- Are user ratings improving or declining over time?
- Are there noticeable differences in review volume between applications?

Uses only data from data/processed/:
- app_kpis.csv
- daily_metrics.csv
- apps_metadata_processed.json (for app titles)
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime
from typing import Dict, Optional

import plotly.graph_objects as go
from plotly.subplots import make_subplots


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROCESSED_DIR = os.path.join(ROOT, "data", "processed")
OUTPUT_DIR = os.path.join(ROOT, "dashboard_output")


def load_app_kpis(csv_path: str) -> list[Dict]:
    """Load app KPIs from CSV."""
    apps = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            try:
                row["num_reviews"] = int(row["num_reviews"])
            except (ValueError, KeyError):
                row["num_reviews"] = 0

            try:
                row["avg_rating"] = float(row["avg_rating"]) if row["avg_rating"] else None
            except (ValueError, KeyError):
                row["avg_rating"] = None

            try:
                row["low_rating_pct"] = float(row["low_rating_pct"]) if row["low_rating_pct"] else None
            except (ValueError, KeyError):
                row["low_rating_pct"] = None

            apps.append(row)
    return apps


def load_daily_metrics(csv_path: str) -> list[Dict]:
    """Load daily metrics from CSV."""
    daily = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["daily_num_reviews"] = int(row["daily_num_reviews"])
            except (ValueError, KeyError):
                row["daily_num_reviews"] = 0

            try:
                row["daily_avg_rating"] = float(row["daily_avg_rating"]) if row["daily_avg_rating"] else None
            except (ValueError, KeyError):
                row["daily_avg_rating"] = None

            daily.append(row)
    return daily


def load_app_metadata(json_path: str) -> Dict[str, str]:
    """Load app metadata and return a mapping of appId -> title."""
    app_titles = {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            apps = json.load(f)
            for app in apps:
                app_id = app.get("appId")
                title = app.get("title", "")
                if app_id:
                    app_titles[app_id] = title
    except Exception as e:
        print(f"Warning: Could not load app metadata: {e}")
    return app_titles


def get_app_display_name(app_id: str, app_titles: Dict[str, str]) -> str:
    """Get display name for an app (title if available, otherwise appId)."""
    return app_titles.get(app_id, app_id)


def create_dashboard() -> None:
    """Create the interactive dashboard."""
    print("Loading data...")
    
    app_kpis_path = os.path.join(PROCESSED_DIR, "app_kpis.csv")
    daily_metrics_path = os.path.join(PROCESSED_DIR, "daily_metrics.csv")
    apps_metadata_path = os.path.join(PROCESSED_DIR, "apps_metadata_processed.json")

    apps = load_app_kpis(app_kpis_path)
    daily = load_daily_metrics(daily_metrics_path)
    app_titles = load_app_metadata(apps_metadata_path)

    print(f"Loaded {len(apps)} apps and {len(daily)} daily records")

    # Filter apps with valid ratings and minimum reviews
    apps_with_ratings = [
        app for app in apps
        if app["avg_rating"] is not None and app["num_reviews"] >= 10
    ]

    # Sort by average rating
    apps_sorted_by_rating = sorted(
        apps_with_ratings,
        key=lambda x: x["avg_rating"],
        reverse=True
    )

    # Prepare daily data for time series
    daily_sorted = sorted(daily, key=lambda x: x["date"])
    dates = [d["date"] for d in daily_sorted]
    daily_ratings = [d["daily_avg_rating"] for d in daily_sorted]
    daily_counts = [d["daily_num_reviews"] for d in daily_sorted]

    # Create subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            "Top 15 Apps by Average Rating",
            "Bottom 15 Apps by Average Rating",
            "Daily Average Rating Over Time",
            "Daily Review Volume Over Time",
            "Top 20 Apps by Review Volume",
            "Rating Distribution: Top vs Bottom Apps"
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "scatter", "secondary_y": False}, {"type": "scatter"}],
            [{"type": "bar"}, {"type": "bar"}],
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )

    # 1. Top 15 apps by rating
    top_15 = apps_sorted_by_rating[:15]
    top_app_names = [get_app_display_name(app["appId"], app_titles) for app in top_15]
    top_ratings = [app["avg_rating"] for app in top_15]

    fig.add_trace(
        go.Bar(
            x=top_ratings,
            y=top_app_names,
            orientation="h",
            marker=dict(color="green", opacity=0.7),
            text=[f"{r:.2f}" for r in top_ratings],
            textposition="outside",
            name="Top Apps"
        ),
        row=1, col=1
    )

    # 2. Bottom 15 apps by rating
    bottom_15 = apps_sorted_by_rating[-15:]
    bottom_app_names = [get_app_display_name(app["appId"], app_titles) for app in bottom_15]
    bottom_ratings = [app["avg_rating"] for app in bottom_15]

    fig.add_trace(
        go.Bar(
            x=bottom_ratings,
            y=bottom_app_names,
            orientation="h",
            marker=dict(color="red", opacity=0.7),
            text=[f"{r:.2f}" for r in bottom_ratings],
            textposition="outside",
            name="Bottom Apps"
        ),
        row=1, col=2
    )

    # 3. Daily average rating over time
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=daily_ratings,
            mode="lines+markers",
            name="Daily Avg Rating",
            line=dict(color="blue", width=2),
            marker=dict(size=3, opacity=0.6),
            hovertemplate="Date: %{x}<br>Avg Rating: %{y:.2f}<extra></extra>"
        ),
        row=2, col=1
    )

    # 4. Daily review volume over time
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=daily_counts,
            mode="lines",
            name="Daily Review Count",
            line=dict(color="purple", width=2),
            fill="tozeroy",
            fillcolor="rgba(128, 0, 128, 0.2)",
            hovertemplate="Date: %{x}<br>Reviews: %{y}<extra></extra>"
        ),
        row=2, col=2
    )

    # 5. Top 20 apps by review volume
    apps_sorted_by_volume = sorted(
        apps,
        key=lambda x: x["num_reviews"],
        reverse=True
    )[:20]
    volume_app_names = [get_app_display_name(app["appId"], app_titles) for app in apps_sorted_by_volume]
    volumes = [app["num_reviews"] for app in apps_sorted_by_volume]

    fig.add_trace(
        go.Bar(
            x=volume_app_names,
            y=volumes,
            marker=dict(color="orange", opacity=0.7),
            text=[f"{v:,}" for v in volumes],
            textposition="outside",
            name="Review Volume"
        ),
        row=3, col=1
    )

    # 6. Rating distribution comparison
    top_10_ratings = [app["avg_rating"] for app in apps_sorted_by_rating[:10] if app["avg_rating"]]
    bottom_10_ratings = [app["avg_rating"] for app in apps_sorted_by_rating[-10:] if app["avg_rating"]]

    fig.add_trace(
        go.Bar(
            x=["Top 10 Apps", "Bottom 10 Apps"],
            y=[sum(top_10_ratings) / len(top_10_ratings) if top_10_ratings else 0,
               sum(bottom_10_ratings) / len(bottom_10_ratings) if bottom_10_ratings else 0],
            marker=dict(color=["green", "red"], opacity=0.7),
            name="Avg Rating Comparison",
            text=[f"{sum(top_10_ratings) / len(top_10_ratings):.2f}" if top_10_ratings else "0",
                  f"{sum(bottom_10_ratings) / len(bottom_10_ratings):.2f}" if bottom_10_ratings else "0"],
            textposition="outside"
        ),
        row=3, col=2
    )

    # Update layout
    fig.update_layout(
        height=1400,
        title_text="Play Store Reviews Analytics Dashboard",
        title_x=0.5,
        title_font_size=20,
        showlegend=False,
        template="plotly_white"
    )

    # Update axes
    fig.update_xaxes(title_text="Average Rating", row=1, col=1)
    fig.update_xaxes(title_text="Average Rating", row=1, col=2)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=2)
    fig.update_xaxes(title_text="Application", row=3, col=1, tickangle=-45)
    fig.update_xaxes(title_text="App Group", row=3, col=2)

    fig.update_yaxes(title_text="Application", row=1, col=1)
    fig.update_yaxes(title_text="Application", row=1, col=2)
    fig.update_yaxes(title_text="Average Rating", row=2, col=1)
    fig.update_yaxes(title_text="Number of Reviews", row=2, col=2)
    fig.update_yaxes(title_text="Number of Reviews", row=3, col=1)
    fig.update_yaxes(title_text="Average Rating", row=3, col=2)

    # Save dashboard
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "dashboard.html")
    fig.write_html(output_path)
    print(f"\nDashboard saved to: {output_path}")
    print(f"Open this file in your web browser to view the interactive dashboard.")

    # Print summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    if apps_with_ratings:
        avg_ratings = [app["avg_rating"] for app in apps_with_ratings if app["avg_rating"]]
        if avg_ratings:
            print(f"\nOverall Average Rating: {sum(avg_ratings) / len(avg_ratings):.2f}")
            print(f"Highest Rated App: {get_app_display_name(top_15[0]['appId'], app_titles)} ({top_15[0]['avg_rating']:.2f})")
            print(f"Lowest Rated App: {get_app_display_name(bottom_15[0]['appId'], app_titles)} ({bottom_15[0]['avg_rating']:.2f})")
    
    total_reviews = sum(app["num_reviews"] for app in apps)
    print(f"\nTotal Reviews Across All Apps: {total_reviews:,}")
    
    if apps_sorted_by_volume:
        print(f"App with Most Reviews: {get_app_display_name(apps_sorted_by_volume[0]['appId'], app_titles)} ({apps_sorted_by_volume[0]['num_reviews']:,} reviews)")
    
    if daily_ratings:
        # Calculate trend (simple linear regression slope)
        recent_ratings = [r for r in daily_ratings[-90:] if r is not None]  # Last 90 days
        if len(recent_ratings) > 1:
            recent_avg = sum(recent_ratings) / len(recent_ratings)
            older_ratings = [r for r in daily_ratings[:90] if r is not None]  # First 90 days
            if older_ratings:
                older_avg = sum(older_ratings) / len(older_ratings)
                trend = recent_avg - older_avg
                trend_text = "improving" if trend > 0.1 else "declining" if trend < -0.1 else "stable"
                print(f"\nRating Trend (comparing first 90 days vs last 90 days): {trend_text} ({trend:+.2f})")


if __name__ == "__main__":
    create_dashboard()

