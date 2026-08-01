-- Write your PostgreSQL query statement below
SELECT tweet_id FROM Tweets
WHERE LENGTH(content) > 15;