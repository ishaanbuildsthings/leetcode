-- Write your PostgreSQL query statement below
SELECT transaction_id
FROM Transactions
WHERE (DATE(day), amount) IN (
SELECT DATE(day), MAX(amount) FROM Transactions GROUP BY DATE(day))
ORDER BY transaction_id;