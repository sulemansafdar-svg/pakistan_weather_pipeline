import os
import json
import pandas as pd


# ================================================================
# WEATHER CODE LABELS
# Shared across both current and hourly cleaning functions
# Based on WMO weather interpretation codes from Open-Meteo API
# ================================================================
WEATHER_LABELS = {
    0:  "Clear",
    1:  "Mainly Clear",
    2:  "Partly Cloudy",
    3:  "Overcast",
    51: "Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    80: "Rain Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Hail"
}


# ================================================================
# FUNCTION 1: Load all raw JSON files from the data/raw folder
# ================================================================
def load_raw_files(folder_path):
    """
    Reads all .json files from the given folder path.
    Returns a list of dictionaries — one dictionary per city.
    """
    all_cities_data = []
    filenames = os.listdir(folder_path)

    for filename in filenames:
        # Skip any non-JSON files that may end up in the folder
        if filename.endswith('.json'):
            full_path = os.path.join(folder_path, filename)

            with open(full_path, 'r', encoding='utf-8') as file:
                file_content = json.load(file)
                all_cities_data.append(file_content)

    return all_cities_data


# ================================================================
# FUNCTION 2: Extract current weather snapshot for all cities
# ================================================================
def extract_current_weather_data(all_data):
    """
    Extracts the current_weather section from each city's raw data.
    Returns a DataFrame with 5 rows — one per city.

    Columns: time, temperature, windspeed, winddirection,
             is_day, weathercode, city, latitude
    """
    current_records = []

    for data in all_data:
        # Copy the current_weather dict to avoid modifying original data
        current = data['current_weather'].copy()

        # Add city name and coordinates — not included in current_weather
        current['city'] = data['city']
        current['latitude'] = data['latitude']

        current_records.append(current)

    return pd.DataFrame(current_records)


# ================================================================
# FUNCTION 3: Extract 7-day hourly forecast for all cities
# ================================================================
def extract_hourly_weather(all_data):
    """
    Extracts the hourly forecast section from each city's raw data.
    Returns a combined DataFrame with 840 rows (168 hours x 5 cities).

    Columns: time, temperature_2m, precipitation,
             windspeed_10m, weathercode, city
    """
    hourly_frames = []

    for data in all_data:
        # hourly is already a dict of lists — pandas converts directly
        hourly_df = pd.DataFrame(data['hourly'])

        # Add city name so we can identify rows after combining
        hourly_df['city'] = data['city']

        hourly_frames.append(hourly_df)

    # Stack all 5 city DataFrames into one and reset index
    return pd.concat(hourly_frames, ignore_index=True)


# ================================================================
# FUNCTION 4: Clean current weather DataFrame
# ================================================================
def clean_current_weather(df):
    """
    Cleans the current weather DataFrame:
    - Drops the 'interval' column (always 900, no analytical value)
    - Renames 'time' to 'recorded_at' for clarity
    - Adds 'load_timestamp' to track when pipeline ran
    - Maps weathercode numbers to human-readable descriptions
    """
    # Work on a copy to protect the original raw DataFrame
    cleaned_df = df.copy()

    # Drop useless interval column
    cleaned_df.drop(columns=['interval'], inplace=True)

    # Rename time to something more descriptive
    cleaned_df.rename(columns={'time': 'recorded_at'}, inplace=True)

    # Record when this pipeline run happened
    cleaned_df['load_timestamp'] = pd.Timestamp.now()

    # Convert numeric weather codes to readable labels
    cleaned_df['weather_description'] = cleaned_df['weathercode'].map(WEATHER_LABELS)

    return cleaned_df


# ================================================================
# FUNCTION 5: Clean hourly weather DataFrame
# ================================================================
def clean_hourly_weather(hourly_df):
    """
    Cleans the hourly forecast DataFrame:
    - Renames columns to cleaner, shorter names
    - Adds 'load_timestamp' to track when pipeline ran
    - Maps weathercode numbers to human-readable descriptions
    """
    # Work on a copy to protect the original raw DataFrame
    cleaned_hourly_df = hourly_df.copy()

    # Rename columns to cleaner names
    cleaned_hourly_df.rename(columns={
        'time':           'forecast_time',
        'temperature_2m': 'temperature',
        'windspeed_10m':  'windspeed'
    }, inplace=True)

    # Record when this pipeline run happened
    cleaned_hourly_df['load_timestamp'] = pd.Timestamp.now()

    # Convert numeric weather codes to readable labels
    cleaned_hourly_df['weather_description'] = (
        cleaned_hourly_df['weathercode'].map(WEATHER_LABELS)
    )

    return cleaned_hourly_df


# ================================================================
# FUNCTION 6: Save both clean DataFrames to CSV
# ================================================================
def save_clean_data(cleaned_df, cleaned_hourly_df):
    """
    Saves the cleaned current and hourly DataFrames to CSV files.
    Output location: data/clean/
    index=False prevents pandas adding an extra numbered column
    """
    # Create output folder if it does not exist
    os.makedirs(r"F:\pakistan_weather_pipeline\data\clean", exist_ok=True)

    cleaned_df.to_csv(
        r"F:\pakistan_weather_pipeline\data\clean\current_weather.csv",
        index=False
    )

    cleaned_hourly_df.to_csv(
        r"F:\pakistan_weather_pipeline\data\clean\hourly_weather.csv",
        index=False
    )

    print("Saved current_weather.csv")
    print("Saved hourly_weather.csv")


# ================================================================
# TEST BLOCK — only runs when file is executed directly
# Not triggered when imported by pipeline.py or Jupyter
# ======================================