-- Write your PostgreSQL query statement below
SELECT 
user_id,
MAX(windows) AS biggest_window
FROM (
SELECT 
uv.user_id,
uv.visit_date,
COALESCE(
    (SELECT MIN(uv2.visit_date) 
    FROM UserVisits uv2 
    WHERE uv2.user_id = uv.user_id AND uv2.visit_date > uv.visit_date),
    DATE '2021-01-01') - uv.visit_date AS windows
FROM UserVisits uv
) t
GROUP BY user_id
ORDER BY user_id;