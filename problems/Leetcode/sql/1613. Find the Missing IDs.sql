-- Write your PostgreSQL query statement below

-- we need to keep feeding rows in over and over until the condition is hit
WITH RECURSIVE items AS (
SELECT 1 AS ids
UNION
SELECT ids + 1 FROM items
WHERE ids < (SELECT MAX(customer_id) FROM Customers))
SELECT ids
FROM items
WHERE ids NOT IN (SELECT customer_id FROM Customers)
ORDER BY ids;