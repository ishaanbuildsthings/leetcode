-- Write your PostgreSQL query statement below
SELECT MAX(num) as num FROM (SELECT num FROM MyNumbers GROUP BY num HAVING COUNT(num) = 1);