-- Write your PostgreSQL query statement below
SELECT
order_date,
ROUND(100 * AVG(CASE WHEN order_date = customer_pref_delivery_date THEN 1 ELSE 0 END), 2) AS immediate_percentage
FROM Delivery
GROUP BY order_date
ORDER BY order_date;