-- Write your PostgreSQL query statement below
SELECT m.symbol AS metal, n.symbol AS nonmetal FROM

    ((SELECT * FROM Elements WHERE type = 'Metal') AS m
    CROSS JOIN 
    (SELECT * FROM Elements WHERE type = 'Nonmetal') AS n
    );