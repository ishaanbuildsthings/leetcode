-- Write your PostgreSQL query statement below
-- put favorite and item brand side by side
WITH cte AS (
SELECT o.seller_id, COUNT(DISTINCT o.item_id) AS num_items
FROM Orders o
JOIN Users u ON o.seller_id = u.seller_id
JOIN Items i ON o.item_id = i.item_id
WHERE i.item_brand != u.favorite_brand
GROUP BY o.seller_id
)
SELECT seller_id, num_items
FROM cte
WHERE num_items = (SELECT MAX(num_items) FROM cte)
ORDER BY seller_id