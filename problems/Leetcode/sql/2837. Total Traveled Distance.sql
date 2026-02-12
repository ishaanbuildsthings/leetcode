-- Write your PostgreSQL query statement below
SELECT uid AS user_id, name, COALESCE(SUM(distance), 0) AS "traveled distance" FROM (
    Select Users.user_id AS uid, name, Rides.distance AS distance FROM Users LEFT JOIN Rides ON Users.user_id = Rides.user_id) GROUP BY uid, name ORDER BY user_id ASC;