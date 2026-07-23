USE master;
GO

-- Drop and recreate the database
IF EXISTS (SELECT 1 FROM sys.databases WHERE name = 'WeatherDB')
BEGIN
    ALTER DATABASE WeatherDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE WeatherDB;
END;
GO
--Create Database DataWarehouse

CREATE DATABASE WeatherDB;
GO
USE WeatherDB;

--Create Schemas
GO
CREATE SCHEMA bronze;
GO
CREATE SCHEMA silver;
GO
CREATE SCHEMA gold;
