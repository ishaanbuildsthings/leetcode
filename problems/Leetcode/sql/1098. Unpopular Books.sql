-- Write your PostgreSQL query statement below
WITH sales AS (
SELECT
book_id,
SUM(quantity) AS tot
FROM Orders
WHERE dispatch_date >= DATE '2018-06-23'
AND dispatch_date <= DATE '2019-06-23'
GROUP BY book_id
)
SELECT
b.book_id,
b.name
FROM Books b
LEFT JOIN sales s
ON b.book_id = s.book_id
WHERE b.available_from <= DATE '2019-05-23'
AND COALESCE(s.tot, 0) < 10;