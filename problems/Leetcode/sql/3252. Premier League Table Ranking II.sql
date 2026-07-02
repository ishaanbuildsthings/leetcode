-- Write your PostgreSQL query statement below

-- first for each team get its raw points
WITH cte1 AS (
SELECT
team_name,
wins * 3 + draws AS points
FROM TeamStats
),

-- get its numeric position and total team count
cte2 AS (
SELECT
team_name,
points,
RANK() OVER (ORDER BY points DESC) AS rank,
COUNT(*) OVER () AS totalTeams
FROM cte1
)


SELECT
team_name,
points,
rank AS position,
CASE
WHEN rank <= CEIL(totalTeams / 3.0) THEN 'Tier 1'
WHEN rank <= CEIL(totalTeams * 2.0 / 3) THEN 'Tier 2'
ELSE 'Tier 3'
END AS tier
FROM cte2
ORDER BY points DESC, team_name ASC;