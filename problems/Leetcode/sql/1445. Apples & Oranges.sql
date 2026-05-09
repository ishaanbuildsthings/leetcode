-- Write your PostgreSQL query statement below
SELECT 
sale_date,
SUM(CASE WHEN fruit = 'apples' THEN sold_num ELSE -1 * sold_num END) AS diff
FROM Sales
GROUP BY sale_date
ORDER BY sale_date;