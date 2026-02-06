-- Write your PostgreSQL query statement below
SELECT tweet_id FROM Tweets WHERE LENGTH(content) > 140 OR regexp_count(content, '@') > 3 OR regexp_count(content, '#') > 3;