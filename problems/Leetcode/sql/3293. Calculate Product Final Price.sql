-- Write your PostgreSQL query statement below
SELECT
p.product_id,
ROUND(p.price * (1 - COALESCE(d.discount, 0) / 100.0),2) AS final_price,
p.category
FROM Products p
LEFT JOIN Discounts d
ON p.category = d.category
ORDER BY p.product_id;