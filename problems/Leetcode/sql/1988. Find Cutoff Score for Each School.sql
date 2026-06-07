-- Write your PostgreSQL query statement below
SELECT
s.school_id,
-- take the min we find or -1 if not valid
COALESCE(MIN(e.score),-1) AS score 
FROM Schools s
LEFT JOIN Exam e
ON e.student_count <= s.capacity
GROUP BY s.school_id;