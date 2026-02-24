CREATE OR REPLACE FUNCTION NthHighestSalary(N INT) RETURNS TABLE (Salary INT) AS $$
BEGIN
  IF N < 1 THEN RETURN QUERY SELECT NULL::INT;
  ELSE
  RETURN QUERY (
    -- Write your PostgreSQL query statement below.
    SELECT DISTINCT e.salary FROM Employee e ORDER BY e.salary DESC LIMIT 1 OFFSET N - 1
      
  );
  END IF;
END;
$$ LANGUAGE plpgsql;