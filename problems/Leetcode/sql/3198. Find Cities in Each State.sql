-- Write your PostgreSQL query statement below
SELECT state, STRING_AGG(city, ', ' ORDER BY city) AS cities FROM cities GROUP BY state;