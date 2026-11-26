-- Write your PostgreSQL query statement below
WITH reviewsIncludingHowManyAreNewer AS (
SELECT
p.employee_id,
p.rating,
(SELECT COUNT(*)
FROM performance_reviews p2
WHERE p2.employee_id = p.employee_id
AND p2.review_date > p.review_date) AS newer_count
FROM performance_reviews p
)
SELECT
e.employee_id,
e.name,
a.rating - c.rating AS improvement_score
FROM reviewsIncludingHowManyAreNewer a
JOIN reviewsIncludingHowManyAreNewer b ON b.employee_id = a.employee_id AND b.newer_count = 1
JOIN reviewsIncludingHowManyAreNewer c ON c.employee_id = a.employee_id AND c.newer_count = 2
JOIN employees e ON e.employee_id = a.employee_id
WHERE a.newer_count = 0
AND c.rating < b.rating
AND b.rating < a.rating
ORDER BY improvement_score DESC, e.name ASC;