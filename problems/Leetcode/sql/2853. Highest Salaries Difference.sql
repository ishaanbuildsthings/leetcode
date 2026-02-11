-- Write your PostgreSQL query statement below
SELECT MAX(salary) - MIN(salary) AS salary_difference FROM (
    SELECT MAX(salary) as salary FROM salaries WHERE department != 'Other' GROUP BY department
);