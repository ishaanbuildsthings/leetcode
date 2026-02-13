SELECT MIN(p2.x - p1.x) AS shortest FROM Point p1 JOIN Point p2 ON p1.x < p2.x;
