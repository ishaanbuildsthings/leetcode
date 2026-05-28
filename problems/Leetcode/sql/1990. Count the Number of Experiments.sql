-- Write your PostgreSQL query statement below

-- hardcoded in case not in table
WITH platforms AS (
SELECT * FROM (VALUES ('Android'), ('IOS'), ('Web')) AS t(platform)
),

experiment_names AS (
SELECT * FROM (VALUES ('Reading'), ('Sports'), ('Programming')) AS t(experiment_name)
)

SELECT
p.platform,
enames.experiment_name,
COUNT(e.experiment_id) AS num_experiments
FROM platforms p
-- every platform x experiment
CROSS JOIN experiment_names enames
 -- preserve empty cells
LEFT JOIN Experiments e
ON e.platform = p.platform
AND enames.experiment_name = e.experiment_name
GROUP BY p.platform, enames.experiment_name;