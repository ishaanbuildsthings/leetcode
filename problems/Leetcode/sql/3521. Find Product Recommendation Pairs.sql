-- Write your PostgreSQL query statement below
-- get the two products and categories that were bought, and how many distinct users in that group of double purchases
SELECT
    p1.product_id AS product1_id,
    p2.product_id AS product2_id,
    pi1.category AS product1_category,
    pi2.category AS product2_category,
    COUNT(DISTINCT p1.user_id) AS customer_count
-- join the table with itself to find a time a user bought 2 different items
FROM ProductPurchases p1
JOIN ProductPurchases p2
    ON p1.user_id = p2.user_id AND p1.product_id < p2.product_id
-- for each of those, add on the product info of each item they bought
JOIN ProductInfo pi1 ON p1.product_id = pi1.product_id
JOIN ProductInfo pi2 ON p2.product_id = pi2.product_id
-- group each double purchase by the 2x2
GROUP BY p1.product_id, p2.product_id, pi1.category, pi2.category
HAVING COUNT(DISTINCT p1.user_id) >= 3
ORDER BY customer_count DESC, product1_id ASC, product2_id ASC;
