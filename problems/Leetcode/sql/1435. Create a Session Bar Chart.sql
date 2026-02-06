-- Write your PostgreSQL query statement below
WITH bins AS (
    SELECT '[0-5>' AS bin UNION ALL
    SELECT '[5-10>' UNION ALL
    SELECT '[10-15>' UNION ALL
    SELECT '15 or more'
),

t AS (
    SELECT
    CASE WHEN duration BETWEEN 0 AND 299 THEN '[0-5>'
    WHEN duration BETWEEN 300 AND 599 then '[5-10>'
    WHEN duration BETWEEN 600 AND 899 THEN '[10-15>'
    WHEN duration >= 900 THEN '15 or more'
    END AS bin,
    session_id
    FROM Sessions
)

SELECT bins.bin AS bin,
COUNT(t.bin) AS total
FROM bins LEFT JOIN t ON bins.bin = t.bin
GROUP BY bins.bin
;