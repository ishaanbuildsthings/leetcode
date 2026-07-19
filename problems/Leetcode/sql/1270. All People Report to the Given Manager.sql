-- Write your PostgreSQL query statement below
SELECT l1.employee_id
FROM Employees l1
JOIN Employees l2 ON l1.manager_id = l2.employee_id
JOIN Employees l3 ON l2.manager_id = l3.employee_id
WHERE l3.manager_id = 1 AND l1.employee_id != 1;