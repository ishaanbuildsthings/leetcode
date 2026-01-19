-- Write your PostgreSQL query statement below
-- SELECT actor_id, director_id FROM (
--     SELECT actor_id, director_id, COUNT(*) AS cnt FROM ActorDirector GROUP BY actor_id, director_id
-- ) AS x WHERE x.cnt >= 3;

SELECT actor_id, director_id FROM ActorDirector GROUP BY actor_id, director_id HAVING COUNT(*) >= 3;