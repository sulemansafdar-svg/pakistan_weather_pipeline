import pandas as pd
import os
from sqlalchemy import create_engine
import urllib

# Database connection setup
params = urllib.parse.quote_plus(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost\\SQLEXPRESS;'
    'DATABASE=WeatherDB;'
    'Trusted_Connection=yes;'
    'TrustServerCertificate=yes;'
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# Cities must match your gold view names exactly
CITIES = ['Islamabad', 'Karachi', 'Lahore', 'Peshawar', 'Quetta']


def get_city_warnings(engine, city):
    """
    Reads from the gold view for one city.
    Returns only rows where alert level is not Normal.
    """
    df = pd.read_sql(
        f"SELECT * FROM gold.{city.lower()}_forecast WHERE alert_level != 'Normal'",
        engine
    )
    
    
    if not df.empty:
        df['city'] = city
        
    return df


def run_warning_engine():
    """
    Loops through all cities.
    Collects all warnings into one combined DataFrame.
    Saves to data/warnings/latest_warnings.csv
    Prints summary to terminal.
    """
    all_warnings = []

    for city in CITIES:
        city_warnings = get_city_warnings(engine, city)

        if len(city_warnings) > 0:
            all_warnings.append(city_warnings)
            print(f"{city}: {len(city_warnings)} warnings found")
        else:
            print(f"{city}: No warnings")

    # Combine all city warning DataFrames into one
    if all_warnings:
        warnings_df = pd.concat(all_warnings, ignore_index=True)

        # Save to CSV
        os.makedirs(r"F:\pakistan_weather_pipeline\data\warnings", exist_ok=True)
        warnings_df.to_csv(
            r"F:\pakistan_weather_pipeline\data\warnings\latest_warnings.csv",
            index=False
        )

        print(f"\n{'='*50}")
        print(f"⚠️  TOTAL ACTIVE WARNINGS: {len(warnings_df)}")
        print(f"{'='*50}")
        get_warning_summary(warnings_df)

    else:
        print("\n✅ No active weather warnings across all cities")


def get_warning_summary(warnings_df):
    """
    Prints a clean grouped summary of active warnings.
    Shows count per city and alert level.
    """
    summary = (
        warnings_df
        .groupby(['city', 'alert_level'])
        .size()
        .reset_index(name='count')
        .sort_values('count', ascending=False)
    )
    print("\nWarning Summary:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    run_warning_engine()
