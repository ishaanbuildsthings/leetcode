-- Write your PostgreSQL query statement below
WITH user_stats AS (
SELECT
user_id,
-- highest plan amount ever
MAX(monthly_amount) AS max_historical_amount,
-- count how many downgrades in history
SUM(CASE WHEN event_type = 'downgrade' THEN 1 ELSE 0 END) AS downgrades,
MAX(event_date) - MIN(event_date) AS days_as_subscriber
FROM subscription_events
GROUP BY user_id
),
latest AS (
-- grab the most recent row per user
SELECT DISTINCT ON (user_id)
user_id, event_type, plan_name, monthly_amount
FROM subscription_events
ORDER BY user_id, event_date DESC, event_id DESC
)
SELECT
l.user_id,
l.plan_name AS current_plan,
l.monthly_amount AS current_monthly_amount,
s.max_historical_amount,
s.days_as_subscriber
FROM latest l
JOIN user_stats s ON l.user_id = s.user_id
WHERE
-- last event is not cancel
l.event_type != 'cancel'
-- at least one downgrade in history
AND s.downgrades >= 1
-- current revenue less than 50% of max
AND l.monthly_amount < s.max_historical_amount * 0.5
-- subscriber for at least 60 days
AND s.days_as_subscriber >= 60
ORDER BY s.days_as_subscriber DESC, l.user_id ASC;