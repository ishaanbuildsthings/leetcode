-- Write your PostgreSQL query statement below
SELECT * FROM Cinema WHERE id % 2 = 1 AND description != 'boring' ORDER BY rating DESC;