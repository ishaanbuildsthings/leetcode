-- Write your PostgreSQL query statement below
SELECT s.student_id
FROM students s
JOIN courses c
ON c.major = s.major
LEFT JOIN enrollments e
ON e.student_id = s.student_id
AND e.course_id  = c.course_id
AND e.grade = 'A'
GROUP BY s.student_id
HAVING COUNT(c.course_id) = COUNT(e.course_id)
ORDER BY s.student_id;