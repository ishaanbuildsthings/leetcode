# Write your MySQL query statement below
SELECT a.player_id, a.event_date,
       (SELECT SUM(b.games_played) FROM Activity b WHERE b.player_id = a.player_id AND b.event_date <= a.event_date) AS games_played_so_far
FROM Activity a;