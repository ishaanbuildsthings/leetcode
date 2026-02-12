-- Write your PostgreSQL query statement below
WITH t AS (
    SELECT sale_id, s.product_id AS product_id, user_id, quantity, price, quantity * price AS total FROM Sales s JOIN Product p ON s.product_id = p.product_id
)

SELECT user_id, SUM(total) AS spending FROM t GROUP BY user_id ORDER BY spending DESC, user_id ASC;