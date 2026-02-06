# Lab 1: Data Engineering Pipeline

A complete data engineering pipeline for extracting, transforming, and analyzing Google Play Store app reviews and metadata.

## Project Overview

This project demonstrates a full data engineering workflow:
1. **Extract**: Scrape app metadata and user reviews from Google Play Store
2. **Transform**: Normalize and process raw data into analytics-ready formats
3. **Load**: Generate CSV files with app-level KPIs and daily metrics
4. **Visualize**: Create an interactive dashboard to explore the data

## Project Structure

```
lab1_data_engineering/
├── data/
│   ├── raw/                    # Raw extracted data
│   │   ├── apps_metadata_raw.json
│   │   └── user_reviews_raw.jsonl
│   └── processed/              # Processed analytics data
│       ├── apps_metadata_processed.json
│       ├── user_reviews_processed.jsonl
│       ├── app_kpis.csv        # App-level KPIs
│       └── daily_metrics.csv   # Daily time series metrics
├── src/
│   ├── extract/                # Data extraction scripts
│   │   ├── extract_large_dataset.py
│   │   └── validate_data.py
│   ├── transform/              # Data transformation scripts
│   │   ├── transform_data.py
│   │   ├── compute_app_kpis.py
│   │   └── compute_daily_metrics.py
│   └── dashboard/              # Dashboard generation
│       └── create_dashboard.py
└── dashboard_output/           # Generated dashboard HTML
    └── dashboard.html
```

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd lab1_data_engineering
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Extract Data

Extract app metadata and reviews from Google Play Store:

```bash
python src/extract/extract_large_dataset.py
```

This will create:
- `data/raw/apps_metadata_raw.json`
- `data/raw/user_reviews_raw.jsonl`

### 2. Transform Data

Normalize and process the raw data:

```bash
python src/transform/transform_data.py
```

This creates processed versions of the data with normalized timestamps, cleaned text, and structured formats.

### 3. Compute Analytics

Generate app-level KPIs:

```bash
python src/transform/compute_app_kpis.py
```

Generate daily metrics:

```bash
python src/transform/compute_daily_metrics.py
```

### 4. Create Dashboard

Generate an interactive dashboard:

```bash
python src/dashboard/create_dashboard.py
```

Open `dashboard_output/dashboard.html` in your web browser to view the visualizations.

## Output Files

### App-Level KPIs (`data/processed/app_kpis.csv`)

Each row represents one application with:
- `appId`: Application identifier
- `num_reviews`: Total number of reviews
- `avg_rating`: Average rating (1-5 scale)
- `low_rating_pct`: Percentage of reviews with rating ≤ 2
- `first_review_date`: Date of first review
- `last_review_date`: Date of most recent review

### Daily Metrics (`data/processed/daily_metrics.csv`)

Each row represents one date with:
- `date`: Calendar date (YYYY-MM-DD)
- `daily_num_reviews`: Number of reviews on that date
- `daily_avg_rating`: Average rating on that date

## Dashboard Features

The interactive dashboard helps answer:
- **Which applications perform best/worst** according to user reviews?
- **Are user ratings improving or declining** over time?
- **Are there noticeable differences** in review volume between applications?

## Technologies Used

- **Python 3.8+**: Core programming language
- **google-play-scraper**: Google Play Store data extraction
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive data visualization

## Data Pipeline Flow

```
Raw Data (JSON/JSONL)
    ↓
Transform & Normalize
    ↓
Processed Data (JSON/JSONL)
    ↓
Compute Aggregations
    ↓
Analytics CSVs (KPIs, Daily Metrics)
    ↓
Visualization Dashboard
```

## Notes

- The pipeline processes data in a streaming fashion for large datasets
- All timestamps are normalized to UTC ISO format
- HTML content is stripped from descriptions
- The dashboard uses only processed data files (separation of concerns)


## Authors

- **Marouane Rbib**
- **Ilyasse El Khazane**

