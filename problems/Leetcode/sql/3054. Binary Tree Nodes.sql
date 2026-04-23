-- Write your PostgreSQL query statement below
SELECT
    N AS "N",
    CASE
    WHEN P IS NULL THEN 'Root'
    WHEN N IN (SELECT P FROM Tree WHERE P IS NOT NULL) THEN 'Inner'
    ELSE 'Leaf'
    END AS "Type"
FROM Tree
ORDER BY N ASC;