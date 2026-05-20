-- Write your PostgreSQL query statement below
SELECT 
query_name,
-- we need the query's rating over its position to get quality
ROUND(AVG(rating::numeric / position), 2) AS quality,
-- poor percentage is the # of queries with rating < 3
ROUND(100.0 * SUM(CASE WHEN rating < 3 THEN 1 ELSE 0 END) / COUNT(*), 2) AS poor_query_percentage
FROM Queries
GROUP BY query_name;