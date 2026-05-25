-- Write your PostgreSQL query statement below
SELECT 
user_id,
ROUND(AVG(CASE WHEN activity_type = 'free_trial' THEN activity_duration END), 2) AS trial_avg_duration,
ROUND(AVG(CASE WHEN activity_type = 'paid' THEN activity_duration END), 2) AS paid_avg_duration
FROM UserActivity ua
WHERE user_id IN (SELECT user_id FROM UserActivity WHERE activity_type = 'paid')
GROUP BY user_id
ORDER BY user_id;