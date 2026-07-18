# extract/fetch_weather.py
import requests
import json
import os
from datetime import datetime

# ============================================================
# City coordinates for 5 major Pakistani cities
# ============================================================
CITIES = {
    "Karachi":   {"lat": 24.8607, "lon": 67.0099},
    "Lahore":    {"lat": 31.5497, "lon": 74.3436},
    "Islamabad": {"lat": 33.7215, "lon": 73.0433},
    "Peshawar":  {"lat": 34.0151, "lon": 71.5249},
    "Quetta":    {"lat": 30.1798, "lon": 66.9750}
}

def fetch_city_weather(city_name, lat, lon):
    """
    Fetches current and 7-day forecast weather data
    for a single city from Open-Meteo API.
    Returns raw JSON dictionary.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,           # current conditions
        "hourly": [
            "temperature_2m",              # hourly temperature
            "precipitation",               # hourly rainfall mm
            "windspeed_10m",               # hourly wind speed
            "weathercode"                  # weather condition code
        ],
        "forecast_days": 7,                # 7 days of hourly data
        "timezone": "Asia/Karachi"         # Pakistan timezone
    }
    
    response = requests.get(url, params=params)
    
    # Check if API call was successful
    if response.status_code != 200:
        print(f"ERROR: API call failed for {city_name}")
        print(f"Status code: {response.status_code}")
        return None
    
    data = response.json()
    data['city'] = city_name    # add city name to raw data
    
    return data

def fetch_all_cities():
    """
    Loops through all 5 cities and fetches weather data.
    Saves each raw response as a JSON file with timestamp.
    Returns list of all raw responses.
    """
    all_data = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("Starting weather data extraction...")
    print("=" * 50)
    
    for city_name, coords in CITIES.items():
        print(f"Fetching data for {city_name}...")
        
        data = fetch_city_weather(
            city_name,
            coords['lat'],
            coords['lon']
        )
        
        if data:
            # Save raw JSON file with city name and timestamp
            filename = f"data/raw/{city_name}_{timestamp}.json"
            os.makedirs("data/raw", exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"  Saved raw data to {filename}")
            all_data.append(data)
        else:
            print(f"  Skipping {city_name} due to API error")
    
    print("=" * 50)
    print(f"Extraction complete. {len(all_data)} cities fetched.")
    return all_data


# ============================================================
# Test the extraction — run this file directly to test
# python extract/fetch_weather.py
# ============================================================
if __name__ == "__main__":
    results = fetch_all_cities()
    
    # Print what the raw data looks like for first city
    if results:
        print("\nSample raw data structure:")
        print(f"City: {results[0]['city']}")
        print(f"Current temperature: {results[0]['current_weather']['temperature']}°C")
        print(f"Current windspeed: {results[0]['current_weather']['windspeed']} km/h")
        print(f"Hourly data points: {len(results[0]['hourly']['time'])}")