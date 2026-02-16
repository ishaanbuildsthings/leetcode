-- Write your PostgreSQL query statement below
SELECT (MAX(tot) - MIN(tot)) AS difference_in_score FROM (
    SELECT SUM(assignment1 + assignment2 + assignment3) AS tot FROM Scores GROUP BY student_id
);