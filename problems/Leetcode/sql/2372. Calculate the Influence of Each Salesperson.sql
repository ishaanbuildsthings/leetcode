-- Write your PostgreSQL query statement below
SELECT
sp.salesperson_id,
sp.name,
COALESCE(SUM(s.price), 0) AS total
FROM Salesperson sp
-- cnonect customer to salesperson
LEFT JOIN Customer c ON c.salesperson_id = sp.salesperson_id
-- connect customer to sale
LEFT JOIN Sales s ON s.customer_id = c.customer_id
GROUP BY sp.salesperson_id, sp.name;