-- Write your PostgreSQL query statement below
WITH firsts AS (
    SELECT DISTINCT ON (customer_id) * FROM Delivery
    ORDER BY customer_id, order_date -- trick to make distinct get the first of each
)

SELECT ROUND(
    100.0 * SUM(CASE WHEN order_date = customer_pref_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 2
) AS immediate_percentage
FROM firsts;