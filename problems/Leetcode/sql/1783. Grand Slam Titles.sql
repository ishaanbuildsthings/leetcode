-- Write your PostgreSQL query statement below
WITH all2 AS (
SELECT Wimbledon AS player_id FROM Championships

UNION ALL

SELECT Fr_open FROM Championships

UNION ALL

SELECT US_open FROM Championships

UNION ALL

SELECT Au_open FROM Championships
)

SELECT p.player_id, p.player_name, COUNT(*) AS grand_slams_count
FROM Players p
JOIN all2 ON p.player_id = all2.player_id
GROUP BY p.player_id, p.player_name