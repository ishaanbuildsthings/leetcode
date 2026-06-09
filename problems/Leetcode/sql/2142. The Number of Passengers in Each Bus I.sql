-- Write your PostgreSQL query statement below
SELECT
b.bus_id,
COUNT(p.passenger_id) AS passengers_cnt
FROM Buses b
LEFT JOIN Passengers p
ON p.arrival_time <= b.arrival_time
AND p.arrival_time > COALESCE(
(SELECT MAX(b2.arrival_time)
FROM Buses b2
WHERE b2.arrival_time < b.arrival_time),
-1
)
GROUP BY b.bus_id, b.arrival_time
ORDER BY b.bus_id;