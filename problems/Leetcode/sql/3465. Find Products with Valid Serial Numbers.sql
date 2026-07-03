-- Write your PostgreSQL query statement below
SELECT product_id, product_name, description
FROM products
-- some sort of space-like character before SN
-- SN followed by 4 digits
-- a hyphen
-- 4 more digits
-- non word char after
WHERE description ~ '\mSN[0-9]{4}-[0-9]{4}\M'
ORDER BY product_id;