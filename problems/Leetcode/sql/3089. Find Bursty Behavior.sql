-- Write your PostgreSQL query statement below
WITH feb_posts AS (
    SELECT * FROM posts WHERE post_date BETWEEN '2024-02-01' AND '2024-02-28'
),

-- this is the 7 day window start dates
windows AS (
SELECT generate_series('2024-02-01'::date, '2024-02-22'::date, '1 day'::interval)::date AS window_start
),

-- we need posts per user per window
counts AS (
SELECT
p.user_id,
w.window_start,
COUNT(p.post_id) AS post_count
FROM windows w
JOIN feb_posts p
ON p.post_date BETWEEN w.window_start AND w.window_start + 6
GROUP BY p.user_id, w.window_start
),

-- get the avg per user
stats AS (
SELECT
user_id,
COUNT(*)::decimal / 4 AS avg
FROM feb_posts
GROUP BY user_id
)

SELECT
s.user_id,
COALESCE(wc.mx, 0) AS max_7day_posts,
ROUND(s.avg, 4) AS avg_weekly_posts
FROM stats s
LEFT JOIN (
-- get max window per user
SELECT user_id, MAX(post_count) AS mx
FROM counts
GROUP BY user_id
) wc ON s.user_id = wc.user_id
WHERE COALESCE(wc.mx, 0) >= 2 * s.avg
ORDER BY s.user_id;