-- Write your PostgreSQL query statement below
WITH goodCustomers AS (
    SELECT customer_id FROM Orders WHERE order_type = 0
)

SELECT * FROM Orders WHERE order_type = 0 OR (
    customer_id NOT IN (SELECT * FROM goodCustomers)
);