-- Write your PostgreSQL query statement below
WITH minMax AS (
SELECT
store_id,
COUNT(*) AS cnt,
MAX(price) AS mx,
MIN(price) AS mn
FROM inventory
GROUP BY store_id
)
SELECT
s.store_id,
s.store_name,
s.location,
up.product_name AS most_exp_product,
down.product_name AS cheapest_product,
ROUND(down.quantity * 1.0 / up.quantity, 2) AS imbalance_ratio
FROM minMax mm
JOIN stores s  ON s.store_id = mm.store_id
JOIN inventory up ON up.store_id = mm.store_id AND up.price = mm.mx
JOIN inventory down ON down.store_id = mm.store_id AND down.price = mm.mn
WHERE mm.cnt >= 3
AND up.quantity < down.quantity
ORDER BY imbalance_ratio DESC, s.store_name ASC;