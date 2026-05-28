-- Write your PostgreSQL query statement below
WITH t AS (
SELECT
order_id,
AVG(quantity)::numeric AS avg,
MAX(quantity) AS mx
FROM OrdersDetails
GROUP BY order_id
)
SELECT order_id
FROM t
WHERE mx > (SELECT MAX(avg) FROM t);