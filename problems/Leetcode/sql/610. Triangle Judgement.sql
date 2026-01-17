-- Write your PostgreSQL query statement below
SELECT
    x,
    y,
    z,
    CASE
        WHEN x + y > z AND x + z > Y and y + z > x
        THEN 'Yes'
        ELSE 'No'
    END AS Triangle
    FROM Triangle;