-- Write your PostgreSQL query statement below
SELECT DISTINCT a.account_id
FROM LogInfo a
JOIN LogInfo b
ON a.account_id = b.account_id
AND a.ip_address < b.ip_address
AND a.login <= b.logout
AND b.login <= a.logout;