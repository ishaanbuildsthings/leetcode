-- Write your PostgreSQL query statement below
SELECT
ad_id,
ROUND(
CASE
-- if no clicks or views ever we are going to assign the ctr to be 0 outright avoids div by 0
WHEN SUM(CASE WHEN action IN ('Clicked', 'Viewed') THEN 1 ELSE 0 END) = 0
THEN 0
ELSE SUM(CASE WHEN action = 'Clicked' THEN 1 ELSE 0 END) * 100.0
/ SUM(CASE WHEN action IN ('Clicked', 'Viewed') THEN 1 ELSE 0 END)
END
, 2) AS ctr
FROM Ads
GROUP BY ad_id
ORDER BY ctr DESC,
ad_id ASC;