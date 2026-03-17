-- Write your PostgreSQL query statement below
WITH f AS ( SELECT airport_id, SUM(flights_count) AS total
    FROM (
        SELECT departure_airport AS airport_id, flights_count FROM Flights
        UNION ALL
        SELECT arrival_airport, flights_count FROM Flights
    ) t
    GROUP BY airport_id
)
SELECT airport_id FROM f WHERE total = (SELECT MAX(total) FROM f);