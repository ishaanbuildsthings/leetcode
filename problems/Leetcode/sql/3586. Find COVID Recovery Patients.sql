-- Write your PostgreSQL query statement below

-- get earliest test date per person
WITH p1 AS (
SELECT patient_id, MIN(test_date) AS mn
FROM covid_tests
WHERE result = 'Positive'
GROUP BY patient_id
),

-- get the negatives after
earlyNeg AS (
SELECT ct.patient_id, MIN(ct.test_date) AS earlyNeg
FROM covid_tests ct
JOIN p1
ON ct.patient_id = p1.patient_id
AND ct.result = 'Negative'
AND ct.test_date > p1.mn
GROUP BY ct.patient_id
)

SELECT
p.patient_id,
p.patient_name,
p.age,
(en.earlyNeg - p1.mn) AS recovery_time
FROM p1
JOIN earlyNeg en ON p1.patient_id = en.patient_id
JOIN patients p ON p.patient_id = p1.patient_id
ORDER BY recovery_time ASC, p.patient_name ASC;