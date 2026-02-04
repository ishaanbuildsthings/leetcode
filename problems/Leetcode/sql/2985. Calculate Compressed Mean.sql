-- Write your PostgreSQL query statement below
SELECT ROUND(tot_items::DECIMAL / tot_orders, 2) AS average_items_per_order FROM
(SELECT SUM(item_count * order_occurrences) AS tot_items, SUM(order_occurrences) AS tot_orders FROM Orders);