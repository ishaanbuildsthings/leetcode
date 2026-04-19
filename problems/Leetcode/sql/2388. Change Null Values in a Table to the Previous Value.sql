-- Write your PostgreSQL query statement below
SELECT c1.id,
(
    SELECT c2.drink
    FROM CoffeeShop c2
    WHERE c2.drink IS NOT NULL
    AND c2.ctid <= c1.ctid
    ORDER BY c2.ctid DESC
    LIMIT 1
) AS drink
FROM CoffeeShop c1
ORDER BY c1.ctid;