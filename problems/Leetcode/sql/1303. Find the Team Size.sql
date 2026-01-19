SELECT employee_id, team_size FROM Employee e JOIN (
    SELECT team_id, COUNT(*) AS team_size FROM Employee GROUP BY team_id) t ON e.team_id = t.team_id;