-- Write your PostgreSQL query statement below
SELECT s1.user_id, s1.steps_date,
ROUND((s1.steps_count + s2.steps_count + s3.steps_count) / 3.0, 2) AS rolling_average
FROM Steps s1
JOIN Steps s2 ON s2.user_id = s1.user_id AND s2.steps_date = s1.steps_date - 1
JOIN Steps s3 ON s3.user_id = s1.user_id AND s3.steps_date = s1.steps_date - 2
ORDER BY s1.user_id, s1.steps_date;