-- Write your PostgreSQL query statement below
SELECT DISTINCT a.user_id
FROM Users a
JOIN Users b
ON a.user_id = b.user_id
AND DATEDIFF(b.created_at, a.created_at) BETWEEN 1 AND 7;