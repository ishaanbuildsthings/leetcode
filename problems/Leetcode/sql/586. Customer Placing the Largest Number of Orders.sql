-- Write your PostgreSQL query statement below
SELECT customer_number FROM (SELECT customer_number, COUNT(*) as cnt FROM Orders GROUP BY Orders.customer_number) ORDER BY cnt DESC LIMIT 1;