# Analytics Dashboard

This dashboard visualizes the processed analytics data from the data engineering pipeline.

## How to View

1. Open `dashboard.html` in any modern web browser (Chrome, Firefox, Edge, Safari)
2. The dashboard is interactive - you can hover over data points, zoom, and pan

## What the Dashboard Shows

The dashboard contains 6 visualizations answering key questions:

### 1. Top 15 Apps by Average Rating
Shows the best-performing applications according to user reviews.

### 2. Bottom 15 Apps by Average Rating
Shows the worst-performing applications according to user reviews.

### 3. Daily Average Rating Over Time
Time series showing whether user ratings are improving or declining over time.

### 4. Daily Review Volume Over Time
Shows the volume of reviews submitted each day, helping identify trends and patterns.

### 5. Top 20 Apps by Review Volume
Highlights applications with the most user engagement (review volume).

### 6. Rating Distribution: Top vs Bottom Apps
Compares average ratings between the top 10 and bottom 10 apps.

## Regenerating the Dashboard

To regenerate the dashboard with updated data:

```bash
cd /home/horhoro/projects/lab1_data_engineering
python src/dashboard/create_dashboard.py
```

This will update `dashboard.html` with the latest data from `data/processed/`.

## Data Sources

The dashboard uses only processed data files:
- `data/processed/app_kpis.csv` - App-level KPIs
- `data/processed/daily_metrics.csv` - Daily aggregated metrics
- `data/processed/apps_metadata_processed.json` - App metadata (for titles)

