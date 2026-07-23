"""
Pakistan Weather Warning Pipeline
==================================
Full end-to-end pipeline:
  1. Extract  — pulls live weather data from Open-Meteo API
  2. Transform — cleans and structures the raw JSON
  3. Load      — inserts clean data into SQL Server bronze layer
  4. Warnings  — reads gold views and generates warning reports

Run this file to execute the complete pipeline:
    python pipeline.py
"""

from extract.fetch_weather import fetch_all_cities
from transform.clean_weather import (
    load_raw_files,
    extract_current_weather_data,
    extract_hourly_weather,
    clean_current_weather,
    clean_hourly_weather,
    save_clean_data
)
from load.load_to_db import run_load
from warnings.warning_engine import run_warning_engine

# Path to raw data folder
RAW_DATA_PATH = r"F:\pakistan_weather_pipeline\data\raw"


def run_pipeline():
    print("=" * 60)
    print("PAKISTAN WEATHER PIPELINE STARTING")
    print("=" * 60)

    # ── STEP 1: EXTRACT ─────────────────────────────────────────
    print("\n[1/4] Extracting weather data from Open-Meteo API...")
    fetch_all_cities()

    # ── STEP 2: TRANSFORM ───────────────────────────────────────
    print("\n[2/4] Transforming raw data...")
    all_data = load_raw_files(RAW_DATA_PATH)

    current_df = clean_current_weather(
        extract_current_weather_data(all_data)
    )
    hourly_df = clean_hourly_weather(
        extract_hourly_weather(all_data)
    )

    save_clean_data(current_df, hourly_df)
    print(f"  Current weather: {len(current_df)} rows")
    print(f"  Hourly forecast: {len(hourly_df)} rows")

    # ── STEP 3: LOAD ─────────────────────────────────────────────
    print("\n[3/4] Loading data into SQL Server bronze layer...")
    run_load()

    # ── STEP 4: WARNINGS ─────────────────────────────────────────
    print("\n[4/4] Running warning engine...")
    run_warning_engine()

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()