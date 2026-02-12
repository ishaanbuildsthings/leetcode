-- Write your PostgreSQL query statement below

WITH a AS (SELECT student_id AS a_id, student_name AS a_name FROM SchoolA),

b AS (SELECT student_id AS b_id, student_name AS b_name FROM SchoolB),

c AS (SELECT student_id AS c_id, student_name AS c_name FROM SchoolC),

t AS (SELECT * FROM (a CROSS JOIN b CROSS JOIN c))

SELECT a_name AS member_A, b_name AS member_B, c_name AS member_C FROM t WHERE (a_id != b_id AND a_id != c_id AND b_id != c_id) AND (a_name != b_name AND a_name != c_name AND b_name != c_name);