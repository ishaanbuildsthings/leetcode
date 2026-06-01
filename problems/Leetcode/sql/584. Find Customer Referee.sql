-- Write your PostgreSQL query statement below
SELECT name FROM Customer WHERE Customer.referee_id != 2 OR Customer.referee_id IS NULL;