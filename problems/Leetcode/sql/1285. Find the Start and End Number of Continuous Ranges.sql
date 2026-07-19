-- Write your PostgreSQL query statement below
SELECT
-- s is going to contain only true starts, so nothing below it exists
s.log_id AS start_id,
-- e is going to be the smallest log ID >= s that has one above it missing
MIN(e.log_id) AS end_id
FROM
-- select 1 just used as convention to indicate if a row exists
(SELECT log_id FROM Logs l1 WHERE NOT EXISTS (SELECT 1 FROM Logs l2 WHERE l2.log_id = l1.log_id - 1)) s

JOIN
-- we look for endings (nothing exists that is 1 above)
(SELECT log_id FROM Logs l1 WHERE NOT EXISTS (SELECT 1 FROM Logs l2 WHERE l2.log_id = l1.log_id + 1)) e

ON e.log_id >= s.log_id
GROUP BY s.log_id
ORDER BY s.log_id;