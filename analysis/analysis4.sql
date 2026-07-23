-- 4. Which city gets the most rainfall this week 
SELECT 
    city,
    ROUND(SUM(precipitation), 2) AS total_rainfall_mm,
    MAX(precipitation) AS single_heaviest_hour
FROM silver.hourly_weather
GROUP BY city;

-- 5. Which hours have dangerous conditions 
SELECT 
    city,
    forecast_time,
    temperature,
    wind_speed,            
    weather_discription,   
    CASE 
         WHEN temperature > 42 THEN 'Danger --Heatwave'
         WHEN temperature > 38 THEN 'Warning --HotWeather'
         WHEN wind_speed > 60  THEN 'Danger --Storm'
         WHEN wind_speed > 40  THEN 'Warning --StrongWind'
         ELSE 'Normal'
    END AS alert_level,    
    DATEPART(hour, forecast_time) AS [hour] 
FROM silver.hourly_weather 
WHERE temperature > 37 OR wind_speed > 39   
ORDER BY city, forecast_time;
