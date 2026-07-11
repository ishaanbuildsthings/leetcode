-- Write your PostgreSQL query statement below

SELECT p.sub_id AS post_id,
COUNT(DISTINCT c.sub_id) AS number_of_comments

-- get all distinct submissions where parent is null means these are basically the mosts
FROM (SELECT DISTINCT sub_id FROM Submissions WHERE parent_id IS NULL) p
LEFT JOIN Submissions c
ON c.parent_id = p.sub_id
GROUP BY p.sub_id
ORDER BY p.sub_id;