-- Write your PostgreSQL query statement below
SELECT
p.name,
COALESCE(SUM(i.rest),0) AS rest,
COALESCE(SUM(i.paid),0) AS paid,
COALESCE(SUM(i.canceled),0) AS canceled,
COALESCE(SUM(i.refunded),0) AS refunded
FROM Product p
LEFT JOIN Invoice i ON p.product_id = i.product_id
GROUP BY p.product_id, p.name
ORDER BY p.name;