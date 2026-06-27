-- Write your PostgreSQL query statement below
SELECT f1.policy_id, f1.state, f1.fraud_score
FROM Fraud f1
WHERE (
SELECT COUNT(*)
FROM Fraud f2
WHERE f2.state = f1.state AND f2.fraud_score > f1.fraud_score) < CEIL(0.05 * (SELECT COUNT(*)
FROM Fraud f3
WHERE f3.state = f1.state
))
ORDER BY f1.state ASC, f1.fraud_score DESC, f1.policy_id ASC;