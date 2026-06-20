-- Write your PostgreSQL query statement below
-- for each team find the # of teams above us, both before and after (in one pass, to optimize constant factor)
SELECT t.team_id, t.name,
(
SELECT
-- # of teams above us with original points
-- we use filter to get two different counts in tandem
COUNT(*) FILTER (
WHERE t2.points > t.points
OR (t2.points = t.points AND t2.name < t.name)
)
-
-- # of teams above us after the points change, diff these to get rank_diff
COUNT(*) FILTER (
WHERE (t2.points + p2.points_change) > (t.points + p.points_change)
OR ((t2.points + p2.points_change) = (t.points + p.points_change) AND t2.name < t.name)
)
FROM TeamPoints t2
JOIN PointsChange p2 ON t2.team_id = p2.team_id
) AS rank_diff
FROM TeamPoints t
JOIN PointsChange p ON t.team_id = p.team_id;