-- Write your PostgreSQL query statement below
WITH stats AS (
SELECT
season_id,
team_id,
team_name,
wins * 3 + draws AS points,
goals_for - goals_against AS goal_difference
FROM SeasonStats
)
SELECT
s.season_id,
s.team_id,
s.team_name,
s.points,
s.goal_difference,
-- basically gets the 1-indexed position
1 + (
SELECT COUNT(*)
FROM stats t
WHERE t.season_id = s.season_id
AND (
t.points > s.points
OR (t.points = s.points AND t.goal_difference > s.goal_difference)
OR (t.points = s.points AND t.goal_difference = s.goal_difference
AND t.team_name < s.team_name)
)
) AS position
FROM stats s
ORDER BY s.season_id ASC,
position ASC,
s.team_name ASC;