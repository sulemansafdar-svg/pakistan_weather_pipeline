--average highest and lowest temperature of each city 
SELECT 
    city,
	ROUND(AVG(temperature),2) AS avg_temp,
	MAX(temperature) AS max_temp,
	MIN(temperature) AS min_temp
FROM silver.hourly_weather 
GROUP BY city


--highest temperature and the city lowest temperture and all cities average 

SELECT 
	ROUND(AVG(temperature),2) AS avg_temp,
	MAX(temperature) AS max_temp,
	MIN(temperature) AS min_temp
FROM silver.hourly_weather
