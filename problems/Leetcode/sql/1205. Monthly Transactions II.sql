-- Write your PostgreSQL query statement below
-- first find all transactions that were approved
WITH txs AS (
SELECT
TO_CHAR(trans_date, 'YYYY-MM') AS month,
country,
1 AS approved_count,
amount AS approved_amount,
0 AS chargeback_count,
0 AS chargeback_amount
FROM Transactions
WHERE state = 'approved'
UNION ALL
-- also we find all the chargebacks
SELECT
TO_CHAR(c.trans_date, 'YYYY-MM') AS month,
t.country,
0 AS approved_count,
0 AS approved_amount,
1 AS chargeback_count,
t.amount AS chargeback_amount
FROM Chargebacks c
-- we need this to find the chargeback country and state since it is not in that table
JOIN Transactions t ON t.id = c.trans_id
)
SELECT
month,
country,
SUM(approved_count) AS approved_count,
SUM(approved_amount) AS approved_amount,
SUM(chargeback_count) AS chargeback_count,
SUM(chargeback_amount) AS chargeback_amount
FROM txs
GROUP BY month, country;