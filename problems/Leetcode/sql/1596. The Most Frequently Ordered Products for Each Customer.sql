-- Write your PostgreSQL query statement below
WITH counts AS (
SELECT customer_id, product_id, COUNT(*) AS c
FROM Orders
GROUP BY customer_id, product_id
)
SELECT counts.customer_id, counts.product_id, p.product_name
FROM counts
JOIN Products p ON counts.product_id = p.product_id
WHERE counts.c = (
SELECT MAX(c2.c)
FROM counts c2
WHERE c2.customer_id = counts.customer_id
);