# Write your MySQL query statement below
SELECT ROUND(AVG(experience_years), 2) AS average_years, project_id FROM Project JOIN Employee ON Project.employee_id = Employee.employee_id GROUP BY project_id;
