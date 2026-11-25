-- Write your PostgreSQL query statement below
SELECT
e1.employee_id,
COUNT(*) AS overlapping_shifts
FROM EmployeeShifts e1
JOIN EmployeeShifts e2
ON  e1.employee_id = e2.employee_id
AND e1.end_time > e2.start_time
AND e1.start_time < e2.start_time
GROUP BY e1.employee_id
ORDER BY e1.employee_id;