-- Write your PostgreSQL query statement below
SELECT
t1.account_id,
t1.day,
(
SELECT SUM(CASE WHEN t2.type = 'Deposit' THEN t2.amount ELSE -1 * t2.amount END)
FROM Transactions t2
WHERE t2.account_id = t1.account_id
AND t2.day <= t1.day
) AS balance
FROM Transactions t1
ORDER BY t1.account_id, t1.day;