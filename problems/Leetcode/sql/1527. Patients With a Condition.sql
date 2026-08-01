-- Write your PostgreSQL query statement below
SELECT *
FROM Patients
WHERE conditions
LIKE 'DIAB1%' OR conditions LIKE '% DIAB1%';