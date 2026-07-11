-- Write your PostgreSQL query statement below
SELECT e.employee_id
FROM Employees e
WHERE e.manager_id IS NOT NULL
AND e.manager_id NOT IN (SELECT employee_id FROM Employees)
AND e.salary < 30_000
ORDER BY e.employee_id;