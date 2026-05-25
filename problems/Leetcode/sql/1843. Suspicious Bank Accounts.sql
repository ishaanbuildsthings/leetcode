-- Write your PostgreSQL query statement below
WITH byMonth AS (
SELECT 
t.account_id,
EXTRACT(YEAR FROM t.day) AS year, -- we grab the year and month to perform math to find adjacent months
EXTRACT(MONTH FROM t.day) AS month,
SUM(t.amount) AS tot,
a.max_income
FROM Transactions t
JOIN Accounts a ON t.account_id = a.account_id
WHERE t.type = 'Creditor'
GROUP BY t.account_id, EXTRACT(YEAR FROM t.day), EXTRACT(MONTH FROM t.day), a.max_income)

SELECT DISTINCT month1.account_id
FROM byMonth month1
JOIN byMonth month2
ON month1.account_id = month2.account_id
AND (month1.year * 12 + month1.month) + 1 = (month2.year * 12 + month2.month)
WHERE month1.tot > month2.max_income
AND month2.tot > month2.max_income;