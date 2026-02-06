# Write your MySQL query statement below
-- SELECT COUNT(*) AS rich_count FROM Store GROUP BY customer_id HAVING MAX(amount) > 500; // bad does the wrong thing

-- SELECT COUNT(*) AS rich_count FROM (
--     SELECT customer_id FROM Store GROUP BY customer_id HAVING MAX(amount) > 500
-- ) t; // works

# Also
SELECT COUNT(DISTINCT customer_id) AS rich_count FROM Store WHERE amount > 500;

