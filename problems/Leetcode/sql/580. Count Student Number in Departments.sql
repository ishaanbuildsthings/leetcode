-- Write your PostgreSQL query statement below
SELECT
d.dept_name,
COUNT(s.student_id) AS student_number
FROM Department d
LEFT JOIN Student s ON s.dept_id = d.dept_id
GROUP BY d.dept_id, d.dept_name
ORDER BY student_number DESC, d.dept_name ASC;