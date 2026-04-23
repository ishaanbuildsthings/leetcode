-- Write your PostgreSQL query statement below
SELECT emp_id, dept
FROM employees e1
WHERE (
SELECT COUNT(DISTINCT e2.salary)
FROM employees e2
WHERE e2.dept = e1.dept
AND e2.salary > e1.salary
) = 1
ORDER BY emp_id;