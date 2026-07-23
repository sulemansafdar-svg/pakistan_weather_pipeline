--which city gets the most rainfall this week 
SELECT 
city,
	ROUND(SUM(precipitation),2) AS total_rainfall_mm,
	MAX(precipitation) AS single_heaviest_hour
FROM silver.hourly_weather
GROUP BY city
