CREATE OR REPLACE FUNCTION getUserIDs(startDate DATE, endDate DATE, minAmount INT) RETURNS INT AS $$
BEGIN
  RETURN (
	  -- Write your PostgreSQL query statement below.
    SELECT COUNT(DISTINCT user_id)
    FROM Purchases
    WHERE time_stamp BETWEEN startDate AND endDate
    AND amount >= minAmount
  );
END;
$$ LANGUAGE plpgsql;



