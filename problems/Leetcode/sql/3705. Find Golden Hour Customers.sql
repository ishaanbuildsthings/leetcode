-- Write your PostgreSQL query statement 
-- first get the ones with the order in one of the two windows (marked on isPeak)
WITH rightTime AS (
SELECT
customer_id,
order_rating,
CASE
WHEN order_timestamp::time BETWEEN '11:00' AND '14:00'
OR order_timestamp::time BETWEEN '18:00' AND '21:00'
THEN 1 ELSE 0
END AS isPeak
FROM restaurant_orders
)
-- out of those orders, get the % by comparing the count to the count of all of them
SELECT
customer_id,
COUNT(*) AS total_orders,
ROUND(100.0 * SUM(isPeak) / COUNT(*)) AS peak_hour_percentage,
ROUND(AVG(order_rating), 2) AS average_rating
FROM rightTime
GROUP BY customer_id
-- keep with the right thresholds
HAVING COUNT(*) >= 3
AND SUM(isPeak) >= 0.6 * COUNT(*)
AND ROUND(AVG(order_rating), 2) >= 4.0
AND COUNT(order_rating) >= 0.5 * COUNT(*)
ORDER BY
average_rating DESC, customer_id DESC;