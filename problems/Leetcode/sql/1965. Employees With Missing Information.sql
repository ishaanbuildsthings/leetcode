-- Write your PostgreSQL query statement below
WITH t AS (
    SELECT COALESCE(e.employee_id, s.employee_id) AS employee_id FROM Employees AS e FULL OUTER JOIN Salaries AS s ON e.employee_id = s.employee_id WHERE e.name IS NULL OR s.salary IS NULL
)

SELECT employee_id FROM t;