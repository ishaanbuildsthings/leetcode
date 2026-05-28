-- Write your PostgreSQL query statement below
SELECT
u.user_id AS buyer_id,
u.join_date,
COUNT(o.order_id) AS orders_in_2019
FROM Users u
LEFT JOIN Orders o
ON u.user_id = o.buyer_id
AND o.order_date >= '2019-01-01'
AND o.order_date < '2020-01-01'
GROUP BY u.user_id, u.join_date
ORDER BY buyer_id;