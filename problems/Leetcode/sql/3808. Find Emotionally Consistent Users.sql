-- Write your PostgreSQL query statement below

-- user<>reaction counts
WITH userreactioncounts AS (
SELECT user_id, reaction, COUNT(*) AS cnt
FROM reactions
GROUP BY user_id, reaction
),

-- total user reactions
totalreacts AS (
SELECT user_id, COUNT(*) AS total
FROM reactions
GROUP BY user_id
)

-- for each user<>reaction pair get its ratio oveer the total and ensure we are 60% (implicitly only 1 per group)
SELECT
urc.user_id,
urc.reaction AS dominant_reaction,
ROUND(urc.cnt * 1.0 / t.total, 2) AS reaction_ratio
FROM userreactioncounts urc
JOIN totalreacts t ON urc.user_id = t.user_id
WHERE t.total >= 5
AND urc.cnt * 1.0 / t.total >= 0.60
ORDER BY reaction_ratio DESC, urc.user_id ASC;