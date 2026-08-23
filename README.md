# EDA Pro

EDA Pro is a Streamlit dashboard for quickly exploring CSV and Excel datasets. It provides data-quality summaries, cleaning controls, interactive distributions, correlation analysis, and cleaned-data export.

## Features

- Upload CSV, XLSX, and XLS files or load a sample dataset
- Review dataset dimensions, data types, missing values, and memory usage
- Drop empty columns, remove duplicates, drop missing rows, or impute numeric values
- Explore histograms, box plots, violin plots, category counts, and pie charts
- Inspect correlation heatmaps, scatter plots, and pair plots
- Cast columns to string, integer, float, category, or datetime
- Download the cleaned dataset as CSV

## Run Locally

```powershell
git clone https://github.com/Ahsan-Qamar-Dev/eda-pro.git
cd eda-pro
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Deployment

This app can be deployed to Streamlit Community Cloud. Select `app.py` as the main file and use `requirements.txt` for dependencies.

## Requirements

- Python 3.9 or newer
- Internet access is required when loading the built-in sample datasets