CREATE OR REPLACE VIEW analytics.v_loan_portfolio AS
SELECT
    l.loan_id, l.account_id, l.loan_date, l.amount, l.duration, l.payments, l.status,
    CASE l.status
        WHEN 'A' THEN 'Terminado al día'
        WHEN 'B' THEN 'Terminado en incumplimiento'
        WHEN 'C' THEN 'Vigente al día'
        WHEN 'D' THEN 'Vigente en mora'
    END AS status_desc,
    (l.status IN ('B', 'D')) AS is_bad,
    d.district_name, d.region, d.avg_salary,
    c.client_id, c.gender,
    EXTRACT(YEAR FROM age(l.loan_date, c.birth_date))::int AS age_at_loan
FROM core.loan l
JOIN core.account  a  ON a.account_id = l.account_id
JOIN core.district d  ON d.district_id = a.district_id
JOIN core.disp     dp ON dp.account_id = l.account_id AND dp.disp_type = 'OWNER'
JOIN core.client   c  ON c.client_id = dp.client_id;