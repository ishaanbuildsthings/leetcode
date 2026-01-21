SELECT product_id, name
FROM Products
WHERE name ~ '(^|[^0-9])[0-9]{3}([^0-9]|$)'
ORDER BY product_id;
