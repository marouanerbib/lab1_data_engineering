# Setup Instructions

## Quick Start

1. **Clone the repository** (if not already done):
```bash
git clone <repository-url>
cd lab1_data_engineering
```

2. **Create and activate virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the pipeline**:
```bash
# Step 1: Extract data
python src/extract/extract_large_dataset.py

# Step 2: Transform data
python src/transform/transform_data.py

# Step 3: Compute analytics
python src/transform/compute_app_kpis.py
python src/transform/compute_daily_metrics.py

# Step 4: Create dashboard
python src/dashboard/create_dashboard.py
```

5. **View dashboard**:
Open `dashboard_output/dashboard.html` in your web browser.

## Troubleshooting

### If google-play-scraper installation fails:
```bash
pip install --upgrade pip
pip install google-play-scraper
```

### If plotly installation fails:
```bash
pip install plotly
```

## Verifying Installation

Check that all dependencies are installed:
```bash
python -c "import google_play_scraper; import plotly; import pandas; print('All dependencies installed!')"
```

