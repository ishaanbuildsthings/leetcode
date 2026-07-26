-- Write your PostgreSQL query statement below

-- find the user who has rated the most movies
(
SELECT u.name AS results
FROM Users u
JOIN MovieRating mr ON mr.user_id = u.user_id
GROUP BY u.user_id, u.name
ORDER BY COUNT(*) DESC, u.name ASC
LIMIT 1
)


UNION ALL

-- find the movie name with highest avg rating in feb 2020
(
SELECT m.title AS results
FROM Movies m
JOIN MovieRating mr ON mr.movie_id = m.movie_id
WHERE mr.created_at >= '2020-02-01' AND mr.created_at < '2020-03-01'
GROUP BY m.movie_id, m.title
ORDER BY AVG(mr.rating) DESC, m.title ASC
LIMIT 1
);


