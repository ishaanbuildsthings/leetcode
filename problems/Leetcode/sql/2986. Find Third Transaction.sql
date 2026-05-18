-- Write your PostgreSQL query statement below
-- get all the date
SELECT 
t.user_id,
t.spend AS third_transaction_spend,
t.transaction_date AS third_transaction_date
FROM Transactions t
-- only include rows where there are exactly 3 matching and the date is <= our date
WHERE (
SELECT COUNT(*) FROM Transactions t2
WHERE t2.user_id = t.user_id 
AND t2.transaction_date <= t.transaction_date
) = 3
-- also only include when we are bigger than any of the previous 2
AND t.spend > (
SELECT MAX(t3.spend) FROM Transactions t3
WHERE t3.user_id = t.user_id 
AND t3.transaction_date < t.transaction_date
)
ORDER BY t.user_id ASC;