-- Write your PostgreSQL query statement below
SELECT name AS "Customers" FROM Customers LEFT JOIN Orders ON Customers.id = Orders.customerId WHERE Orders.id IS NULL;