-- Write your PostgreSQL query statement below
SELECT
    country_name,
    CASE
        WHEN AVG(weather_state) >= 25 THEN 'Hot'
        WHEN AVG(weather_state) <= 15 THEN 'Cold'
        ELSE 'Warm'
    END AS weather_type
    FROM Countries LEFT JOIN Weather ON Countries.country_id = Weather.country_id
    WHERE day >= DATE '2019-11-01'
  AND day <  DATE '2019-12-01'
  GROUP BY country_name;