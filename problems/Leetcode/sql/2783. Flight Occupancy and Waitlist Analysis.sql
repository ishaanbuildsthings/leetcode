-- Write your PostgreSQL query statement below
-- get a bunch of rows for passenger <-> flight all together
-- group them by the flight id/capacity (the same)
-- in that group we count the # of passengers and compare it to the flight capacity
SELECT 
f.flight_id,
LEAST(COUNT(p.passenger_id), f.capacity) AS booked_cnt,
GREATEST(COUNT(p.passenger_id) - f.capacity, 0) AS waitlist_cnt
FROM Flights f
LEFT JOIN Passengers p ON f.flight_id = p.flight_id
GROUP BY f.flight_id, f.capacity
ORDER BY f.flight_id;