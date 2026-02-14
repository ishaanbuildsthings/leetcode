SELECT e.user_id FROM emails e JOIN texts t ON e.email_id = t.email_id WHERE t.
signup_action = 'Verified' AND t.action_date::date = e.signup_date::date + INTERVAL
'1 day' ORDER BY e.user_id;
