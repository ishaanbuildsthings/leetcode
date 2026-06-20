-- Write your PostgreSQL query statement below
SELECT e.business_id
FROM Events e
JOIN (
SELECT event_type, AVG(occurrences) AS avg
FROM Events
GROUP BY event_type
) a
ON e.event_type = a.event_type
WHERE e.occurrences > a.avg
GROUP BY e.business_id
HAVING COUNT(*) > 1;