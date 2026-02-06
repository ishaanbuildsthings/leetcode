-- Write your PostgreSQL query statement below
SELECT CASE WHEN ny > ca THEN 'New York University' WHEN ca > ny THEN 'California University' ELSE 'No Winner' END AS winner FROM (
    SELECT COUNT(*) FROM NewYork WHERE score >= 90
) ny,
(SELECT COUNT(*) FROM California WHERE score >= 90) ca;