-- Write your PostgreSQL query statement below
WITH comb AS (
    SELECT caller_id AS id, duration FROM Calls

    UNION ALL

    SELECT callee_id AS id, duration FROM Calls
)

SELECT c.name AS country
FROM comb cmb
JOIN Person p on p.id = cmb.id
JOIN Country c ON c.country_code = LEFT(p.phone_number, 3)
GROUP BY c.name

HAVING AVG(cmb.duration) > (
    SELECT AVG(duration) FROM comb
);