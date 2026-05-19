-- Write your PostgreSQL query statement below
-- we are going to get the average PER day and average all of those
SELECT ROUND(AVG(daily_per), 2) AS average_daily_percent
FROM (
SELECT
action_date,
-- get the # of distinct posts that were removed compared to # of posts in that day
COUNT(DISTINCT CASE WHEN post_id IN (SELECT post_id FROM Removals) THEN post_id END) * 100.0
/ COUNT(DISTINCT post_id) AS daily_per
FROM Actions
WHERE action = 'report' AND extra = 'spam'
-- get the average per day
GROUP BY action_date
) t;