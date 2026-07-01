-- Write your PostgreSQL query statement below

SELECT
t.team_id,
t.team_name,
COALESCE(SUM(points.points),0) AS num_points
FROM Teams t

LEFT JOIN (
    -- first get it from the host
    SELECT host_team AS team_id,
    CASE WHEN host_goals > guest_goals THEN 3
    WHEN host_goals = guest_goals THEN 1
    ELSE 0 END AS points
    FROM Matches

    UNION ALL

    -- stack on top of guest
    SELECT guest_team AS team_id,
    CASE WHEN guest_goals > host_goals THEN 3
    WHEN guest_goals = host_goals THEN 1
    ELSE 0 END AS points

    FROM Matches
) points ON points.team_id = t.team_id

GROUP BY t.team_id, t.team_name
ORDER BY num_points DESC, t.team_id ASC;