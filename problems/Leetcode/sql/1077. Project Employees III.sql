-- Write your PostgreSQL query statement below
SELECT
p.project_id,
p.employee_id
FROM Project p

JOIN Employee e ON p.employee_id = e.employee_id

WHERE e.experience_years = (
    SELECT MAX(e2.experience_years) FROM Project p2 JOIN Employee e2 ON p2.employee_id = e2.employee_id WHERE p2.project_id = p.project_id
);