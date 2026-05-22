-- Write your PostgreSQL query statement below
SELECT 
LEAST(from_id, to_id) AS person1,
GREATEST(from_id, to_id) AS person2,
SUM(duration) AS total_duration,
COUNT(*) AS call_count
FROM Calls
GROUP BY LEAST(from_id, to_id), GREATEST(from_id, to_id);