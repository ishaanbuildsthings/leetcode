-- Write your PostgreSQL query statement below

-- for each city for each hour get its counts
WITH hrCounts AS (
SELECT
city,
EXTRACT(HOUR FROM call_time) AS peak_calling_hour,
COUNT(*) AS number_of_calls
FROM Calls
GROUP BY city, EXTRACT(HOUR FROM call_time)
),

-- for each city get the max count from the per-city per hour counts
mxCounts AS (
SELECT city, MAX(number_of_calls) AS mx
FROM hrCounts
GROUP BY city
)

-- get the city, its peak hour, its number, as long as it equals the max
SELECT hc.city, hc.peak_calling_hour, hc.number_of_calls
FROM hrCounts hc
JOIN mxCounts mc
ON hc.city = mc.city AND hc.number_of_calls = mc.mx
ORDER BY hc.peak_calling_hour DESC, hc.city DESC;