CREATE OR REPLACE FUNCTION getUserIDs(startDate DATE, endDate DATE, minAmount INT)
RETURNS TABLE (user_id INT) AS $$
BEGIN
  RETURN QUERY (
      -- Write your PostgreSQL query statement below.
      SELECT DISTINCT p.user_id
      FROM Purchases p
      WHERE p.time_stamp >= startDate
      AND p.time_stamp < endDate
      AND p.amount >= minAmount
      ORDER BY p.user_id
  );
END;
$$ LANGUAGE plpgsql;