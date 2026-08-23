# EDA Pro

EDA Pro is a Streamlit dashboard for quickly exploring CSV and Excel datasets. It provides data-quality summaries, cleaning controls, interactive distributions, correlation analysis, and cleaned-data export.

## Live Demo

Try the deployed app here:

**[Open EDA Pro](https://eda-pro-dashboard.streamlit.app/)**

## Features

- Upload CSV, XLSX, and XLS files or load a sample dataset
- Review dataset dimensions, data types, missing values, and memory usage
- Drop empty columns, remove duplicates, drop missing rows, or impute numeric values
- Explore histograms, box plots, violin plots, category counts, and pie charts
- Inspect correlation heatmaps, scatter plots, and pair plots
- Cast columns to string, integer, float, category, or datetime
- Download the cleaned dataset as CSV

## Run Locally

Use this only when developing or testing changes on your computer.

```powershell
git clone https://github.com/Ahsan-Qamar-Dev/eda-pro.git
cd eda-pro
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser. Localhost is only available on the computer running Streamlit.

## Deployment

This app is deployed on Streamlit Community Cloud at [eda-pro-dashboard.streamlit.app](https://eda-pro-dashboard.streamlit.app/). The deployment uses the `main` branch and `app.py` as the main file. Dependencies are installed from `requirements.txt`.

## Requirements

- Python 3.9 or newer
- Internet access is required when loading the built-in sample datasets