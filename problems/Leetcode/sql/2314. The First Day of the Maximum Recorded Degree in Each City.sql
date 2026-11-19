-- Write your PostgreSQL query statement below
SELECT DISTINCT ON (city_id) city_id, day, degree
FROM Weather
ORDER BY city_id, degree DESC, day;