-- Write your PostgreSQL query statement below
WITH state_data AS (
    SELECT
    state,
    STRING_AGG(city, ', ' ORDER BY city) AS cities,
    COUNT(*) AS city_count,
    SUM(CASE WHEN UPPER(LEFT(city, 1)) = UPPER(LEFT(state, 1)) THEN 1 ELSE 0 END) AS matching_letter_count
    FROM cities
    GROUP BY state
)
SELECT state, cities, matching_letter_count
FROM state_data
WHERE city_count >= 3 AND matching_letter_count >= 1
ORDER BY matching_letter_count
DESC, state ASC;