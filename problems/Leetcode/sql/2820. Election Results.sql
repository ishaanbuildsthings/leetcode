-- Write your PostgreSQL query statement below

-- first get the counts that each voter made
WITH counts AS (
SELECT voter, COUNT(*) AS cnt
FROM Votes
WHERE candidate IS NOT NULL
GROUP BY voter
),

-- now we want the weighted sums for every candidate
-- we assign the weighted value for each candidate and group by the candidates
totals AS (
SELECT v.candidate, SUM(1.0 / vc.cnt) AS votes
FROM Votes v
JOIN counts vc ON v.voter = vc.voter
WHERE v.candidate IS NOT NULL
GROUP BY v.candidate
)

SELECT candidate
FROM totals
WHERE votes = (SELECT MAX(votes) FROM totals)
ORDER BY candidate ASC;