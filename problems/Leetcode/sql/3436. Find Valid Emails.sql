-- Write your PostgreSQL query statement below
SELECT user_id, email
FROM Users
-- ^ checks it is at the beginning
-- letters + digits + underscores
-- @ sign
-- letters only
-- .com
WHERE email ~ '^[A-Za-z0-9_]+@[A-Za-z]+\.com$'
ORDER BY user_id;