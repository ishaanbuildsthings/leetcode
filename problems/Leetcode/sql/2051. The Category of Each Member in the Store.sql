-- Write your PostgreSQL query statement below
-- join every member to every visit to every purchase
-- now we have one big combined table
-- we will group by member id to get a unique result for each of them
-- in a group we perform an aggregator
-- we look at the total count of their visits as a ratio to give the category
SELECT
m.member_id,
m.name,
CASE
WHEN COUNT(v.visit_id) = 0 THEN 'Bronze'
WHEN 100.0 * COUNT(p.visit_id) / COUNT(v.visit_id) >= 80 THEN 'Diamond'
WHEN 100.0 * COUNT(p.visit_id) / COUNT(v.visit_id) >= 50 THEN 'Gold'
ELSE 'Silver'
END AS category
FROM Members m
LEFT JOIN Visits v ON m.member_id = v.member_id
LEFT JOIN Purchases p ON v.visit_id = p.visit_id
GROUP BY m.member_id, m.name