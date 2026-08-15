-- Write your PostgreSQL query statement below

WITH sz AS (
    SELECT dep_id, COUNT(*) AS cnt
    FROM Employees
    GROUP BY dep_id
)

SELECT e.emp_name AS manager_name, e.dep_id
FROM Employees e
JOIN sz ON sz.dep_id = e.dep_id
WHERE e.position = 'Manager'
AND sz.cnt = (SELECT MAX(cnt) FROM sz)
ORDER BY e.dep_id;