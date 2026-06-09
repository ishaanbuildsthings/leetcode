-- Write your PostgreSQL query statement below
WITH bus AS (
SELECT
b.bus_id,
b.arrival_time,
COALESCE(
(SELECT MAX(b2.arrival_time)
FROM Buses b2
WHERE b2.arrival_time < b.arrival_time),
-1
) AS prev
FROM Buses b
)
SELECT
bus.bus_id,
COUNT(p.passenger_id) AS passengers_cnt
FROM bus
LEFT JOIN Passengers p
ON p.arrival_time <= bus.arrival_time
AND p.arrival_time > bus.prev
GROUP BY bus.bus_id, bus.arrival_time
ORDER BY bus.bus_id;