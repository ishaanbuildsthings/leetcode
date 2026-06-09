-- Write your PostgreSQL query statement below
SELECT
p.product_id,
ROUND(
COALESCE(SUM(u.units * p.price)::numeric / NULLIF(SUM(u.units), 0), 0),
2
) AS average_price
FROM Prices p
LEFT JOIN UnitsSold u
ON u.product_id = p.product_id
AND u.purchase_date BETWEEN p.start_date AND p.end_date
GROUP BY p.product_id;