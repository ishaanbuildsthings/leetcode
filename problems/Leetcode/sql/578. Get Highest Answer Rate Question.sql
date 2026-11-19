-- Write your PostgreSQL query statement below
SELECT question_id AS survey_log
FROM SurveyLog
GROUP BY question_id
ORDER BY
SUM(CASE WHEN action = 'answer' THEN 1 ELSE 0 END)::numeric
/ SUM(CASE WHEN action = 'show' THEN 1 ELSE 0 END) DESC,
question_id
LIMIT 1;