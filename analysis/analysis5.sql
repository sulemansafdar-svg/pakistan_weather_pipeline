--average temperature per day by city 

SELECT 
    city,
    LEFT(forecast_time,10) AS date,
    ROUND(AVG(temperature),2) AS avg_temp,
    ROUND(AVG(wind_speed),2) AS avg_wind
FROM silver.hourly_weather
GROUP BY city,LEFT(forecast_time,10) 
ORDER BY city,date
