# Write your MySQL query statement below


SELECT
LOWER(TRIM(product_name)) AS product_name,
SUBSTRING(sale_date, 1, 7) AS sale_date,
COUNT(*) AS total
FROM Sales
-- i was getting a naming conflict here with product_name
-- so we put the command directly in the group by
GROUP BY LOWER(TRIM(product_name)), SUBSTRING(sale_date, 1, 7)
ORDER BY product_name, sale_date;