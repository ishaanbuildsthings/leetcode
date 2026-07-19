-- Write your PostgreSQL query statement below
SELECT
s1.gender,
s1.day,
(SELECT SUM(s2.score_points) FROM Scores s2 WHERE s2.gender = s1.gender AND s2.day <= s1.day) AS total
FROM Scores s1
ORDER BY s1.gender, s1.day;