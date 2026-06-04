-- Write your PostgreSQL query statement below
-- for each col we look at the biggest on left and right, take the smallest of them
SELECT SUM(LEAST(leftMax, rightMax) - height) AS total_trapped_water
FROM (
SELECT h.id,
h.height,
-- for all h2s before us we get its height else null
MAX(CASE WHEN h2.id <= h.id THEN h2.height END) AS leftMax,
MAX(CASE WHEN h2.id >= h.id THEN h2.height END) AS rightMax
FROM Heights h
CROSS JOIN Heights h2
GROUP BY h.id, h.height
) t;