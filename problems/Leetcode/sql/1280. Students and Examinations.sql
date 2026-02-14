SELECT s.student_id, s.student_name, sub.subject_name, COUNT(Examinations.student_id) AS
attended_exams FROM Students s CROSS JOIN Subjects sub LEFT JOIN Examinations ON s.student_id =
Examinations.student_id AND sub.subject_name = Examinations.subject_name GROUP BY s.student_id,
student_name, sub.subject_name;
