-- Write your PostgreSQL query statement below
WITH companyMax AS (
SELECT company_id, MAX(salary) AS maxSalary
FROM Salaries
GROUP BY company_id
)
SELECT
s.company_id,
s.employee_id,
s.employee_name,
ROUND(s.salary * (1 - CASE WHEN cm.maxSalary < 1000 THEN 0.00 WHEN cm.maxSalary <= 10000 THEN 0.24 ELSE 0.49 END)) AS salary
FROM Salaries s
JOIN companyMax cm ON cm.company_id = s.company_id;