-- Write your PostgreSQL query statement below
SELECT
combined.week_of_month,
combined.membership,
COALESCE(SUM(p.amount_spend), 0) AS total_amount
FROM (VALUES
(1,'Premium'),(1,'VIP'),(2,'Premium'),(2,'VIP'),(3,'Premium'),(3,'VIP'),(4,'Premium'),(4,'VIP')) AS combined(week_of_month, membership)
LEFT JOIN Users u
ON u.membership = combined.membership
LEFT JOIN Purchases p
ON p.user_id = u.user_id
-- friday check
AND EXTRACT(DOW FROM p.purchase_date) = 5
AND CEIL(EXTRACT(DAY FROM p.purchase_date) / 7.0) = combined.week_of_month
GROUP BY combined.week_of_month, combined.membership
ORDER BY combined.week_of_month, combined.membership;