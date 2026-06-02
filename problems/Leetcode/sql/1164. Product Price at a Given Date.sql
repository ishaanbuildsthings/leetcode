-- Write your PostgreSQL query statement below
SELECT
pid.product_id,
COALESCE((
SELECT p.new_price
FROM Products p
WHERE p.product_id = pid.product_id
AND p.change_date <= '2019-08-16'
ORDER BY p.change_date DESC
LIMIT 1
), 10) AS price
FROM (SELECT DISTINCT product_id FROM Products) pid;