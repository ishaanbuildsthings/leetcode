-- Write your PostgreSQL query statement below
WITH pcnt AS (
    SELECT COUNT(*) AS cnt FROM Product
)
SELECT customer_id
FROM Customer
GROUP BY customer_id
HAVING COUNT(DISTINCT product_key) = (SELECT cnt FROM pcnt);