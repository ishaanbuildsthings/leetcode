-- Write your PostgreSQL query statement below
WITH lastDayPerProduct AS (
SELECT
product_id,
MAX(order_date) AS lastDay
FROM Orders
GROUP BY product_id
)
SELECT
p.product_name,
o.product_id,
o.order_id,
o.order_date
FROM Orders o
JOIN lastDayPerProduct l
ON l.product_id = o.product_id
AND l.lastDay = o.order_date
JOIN Products p ON p.product_id = o.product_id
ORDER BY p.product_name ASC, o.product_id ASC, o.order_id ASC;