-- Write your PostgreSQL query statement below
SELECT
    s.name FROM
    SalesPerson s
    LEFT JOIN Orders o ON s.sales_id = o.sales_id
    LEFT JOIN Company c ON o.com_id = c.com_id
    WHERE s.name NOT IN
        (SELECT
            s.name FROM SalesPerson s
            LEFT JOIN Orders o ON s.sales_id = o.sales_id
            LEFT JOIN Company c ON o.com_id = c.com_id
            WHERE c.name = 'RED' GROUP BY s.name
        )
    GROUP BY s.name;