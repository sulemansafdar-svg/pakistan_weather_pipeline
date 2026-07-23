import pandas as pd
from sqlalchemy import create_engine, MetaData, Column, Table, String
from sqlalchemy.orm import Session
import urllib


# ================================================================
# DATABASE CONNECTION
# Uses Windows Authentication — no username or password needed
# TrustServerCertificate bypasses SSL certificate errors on local
# ================================================================
def get_engine():
    params = urllib.parse.quote_plus(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'
        'DATABASE=WeatherDB;'
        'Trusted_Connection=yes;'
        'TrustServerCertificate=yes;'
    )
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    return engine


# ================================================================
# SCHEMA DEFINITION
# All columns are String — this is the Bronze layer (raw as-is)
# Bronze = land data first, enforce types in Silver later
# ================================================================
meta = MetaData()

bronze_current_weather = Table(
    'current_weather',
    meta,
    Column('recorded_at',         String(50)),
    Column('temperature',         String(50)),
    Column('windspeed',           String(50)),
    Column('winddirection',       String(100)),
    Column('is_day',              String(50)),
    Column('weathercode',         String(50)),    
    Column('city',                String(50)),
    Column('latitude',            String(100)),
    Column('load_timestamp',      String(100)),
    Column('weather_description', String(150)),   
    schema='bronze'
)

bronze_hourly_weather = Table(
    'hourly_weather',
    meta,
    Column('forcast_time',      String(100)),    
    Column('temperature',        String(100)),    
    Column('precipitation',      String(100)),
    Column('windspeed',          String(100)),
    Column('weathercode',        String(100)),
    Column('city',               String(100)),
    Column('load_timestamp',     String(100)),
    Column('weather_discription', String(100)), 
    schema='bronze'
)


# ================================================================
# INIT DATABASE
# Creates both tables in the bronze schema if they do not exist
# Run this once before loading any data
# Requires: USE WeatherDB; CREATE SCHEMA bronze; in SSMS first
# ================================================================
def init_database(engine):
    meta.create_all(engine)
    print("Database tables ready")


# ================================================================
# LOAD FILE
# Reads a CSV and inserts into the target SQL Server table
# Truncates the table first to avoid duplicate data on each run
# chunk_size controls how many rows inserted per batch
# ================================================================
def load_file(file_path, target_table, engine, chunk_size=50000):
    # Read clean CSV into DataFrame
    df = pd.read_csv(file_path)
    print(f"Read {len(df)} rows from {file_path}")
    df = df.fillna("").astype(str)
    # Convert rows to list of dicts for SQLAlchemy insert
    records = df.to_dict(orient='records')

    with Session(engine) as session:
        # Clear existing data before inserting fresh data
        session.execute(target_table.delete())

        # Insert in chunks — handles large files efficiently
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i + chunk_size]
            session.execute(target_table.insert(), chunk)
            print(f"Inserted rows {i} to {i + len(chunk)}")

        # Commit all inserts as one transaction
        session.commit()
        print(f"Successfully loaded into bronze.{target_table.name}")


# ================================================================
# RUN LOAD
# Main entry point — connects, initialises tables, loads both files
# ================================================================
def run_load():
    engine = get_engine()
    init_database(engine)

    # Load current weather snapshot (5 rows)
    load_file(
        file_path=r"F:\pakistan_weather_pipeline\data\clean\current_weather.csv",
        target_table=bronze_current_weather,
        engine=engine
    )

    # Load 7-day hourly forecast (840 rows)
    load_file(
        file_path=r"F:\pakistan_weather_pipeline\data\clean\hourly_weather.csv",
        target_table=bronze_hourly_weather,
        engine=engine
    )


# ================================================================
# TEST BLOCK — only runs when file is executed directly
# ================================================================
if __name__ == "__main__":
    run_load()