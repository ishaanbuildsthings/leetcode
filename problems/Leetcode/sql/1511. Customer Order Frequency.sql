-- Write your PostgreSQL query statement below

SELECT c.customer_id, c.name
FROM Customers c
JOIN Orders o ON o.customer_id = c.customer_id
JOIN Product p ON p.product_id = o.product_id
GROUP BY c.customer_id, c.name
HAVING SUM(CASE WHEN o.order_date BETWEEN '2020-06-01' AND '2020-06-30' THEN o.quantity * p.price ELSE 0 END) >= 100
   AND SUM(CASE WHEN o.order_date BETWEEN '2020-07-01' AND '2020-07-31' THEN o.quantity * p.price ELSE 0 END) >= 100;