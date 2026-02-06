-- Write your PostgreSQL query statement below
SELECT bit_and(permissions) AS common_perms, bit_or(permissions) AS any_perms FROM user_permissions;