-- Write your PostgreSQL query statement below
SELECT score, DENSE_RANK() OVER (ORDER BY score DESC) AS "rank" FROM Scores ORDER BY score DESC