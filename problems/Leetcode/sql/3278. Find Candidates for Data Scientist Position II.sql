-- Write your PostgreSQL query statement below

-- how many skills each project needs
WITH numSkills AS (
SELECT project_id, COUNT(*) AS need
FROM Projects
GROUP BY project_id
),

-- for every candidate <> project pair we need a score for just this row
VAL AS (
SELECT
p.project_id,
c.candidate_id,
100 + SUM(CASE WHEN c.proficiency > p.importance THEN 10 WHEN c.proficiency < p.importance THEN -5 ELSE 0 END) AS score,
COUNT(*) AS cnt
FROM Projects p
JOIN Candidates c ON c.skill = p.skill
GROUP BY p.project_id, c.candidate_id
),

-- we need those who have all the skills
goodCandidates AS (
SELECT v.project_id, v.candidate_id, v.score
FROM VAL v
JOIN numSkills ns ON ns.project_id = v.project_id
WHERE v.cnt = ns.need
)

SELECT gc1.project_id, gc1.candidate_id, gc1.score
FROM goodCandidates gc1
WHERE NOT EXISTS (
SELECT 1
FROM goodCandidates gc2
WHERE gc2.project_id = gc1.project_id
AND (gc2.score > gc1.score
OR (gc2.score = gc1.score AND gc2.candidate_id < gc1.candidate_id))
)
ORDER BY gc1.project_id;