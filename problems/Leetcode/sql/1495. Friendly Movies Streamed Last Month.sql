-- Write your PostgreSQL query statement below
SELECT DISTINCT c.title
FROM Content c
JOIN TVProgram tv ON c.content_id = tv.content_id
WHERE c.Kids_content = 'Y'
AND c.content_type = 'Movies'
AND tv.program_date >= '2020-06-01'
AND tv.program_date < '2020-07-01';