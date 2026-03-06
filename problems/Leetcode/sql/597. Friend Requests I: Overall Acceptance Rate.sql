-- Write your PostgreSQL query statement below
SELECT ROUND(
    COALESCE(
        (SELECT COUNT(*) FROM (SELECT DISTINCT requester_id, accepter_id FROM RequestAccepted))::numeric /
        NULLIF((SELECT COUNT(*) FROM (SELECT DISTINCT sender_id, send_to_id FROM FriendRequest)), 0)
        , 0
    ), 2
) AS accept_rate;