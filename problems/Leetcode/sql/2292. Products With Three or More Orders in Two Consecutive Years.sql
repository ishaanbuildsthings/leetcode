-- Write your PostgreSQL query statement below
-- first we get every product <> year combo that has >= 3
WITH product_by_year AS (
    -- dont really know how these extracts work
SELECT product_id, EXTRACT(YEAR FROM purchase_date) AS year, COUNT(*) AS cnt
FROM Orders
GROUP BY product_id, EXTRACT(YEAR FROM purchase_date)
HAVING COUNT(*) >= 3
)
-- now do the self join trick and compare
SELECT DISTINCT a.product_id
FROM product_by_year a
JOIN product_by_year b
  ON a.product_id = b.product_id
 AND b.year = a.year + 1;