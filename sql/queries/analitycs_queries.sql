-- Q1. Composición de la cartera por estado (agregación + ventana sobre agregados)
SELECT status, status_desc, COUNT(*) AS loans, SUM(amount) AS total_amount,
       ROUND(100.0 * SUM(amount) / SUM(SUM(amount)) OVER (), 2) AS pct_of_portfolio
FROM analytics.v_loan_portfolio
GROUP BY status, status_desc
ORDER BY status;

-- Q2. Tasa de mala cartera por región (B o D)
SELECT region, COUNT(*) AS loans,
       ROUND(100.0 * AVG(is_bad::int), 2) AS bad_rate_pct,
       SUM(is_bad::int) AS bad_loans
FROM analytics.v_loan_portfolio
GROUP BY region
ORDER BY bad_rate_pct DESC;

-- Q3. Mala cartera por plazo y rango de edad (CASE + HAVING)
SELECT duration,
       CASE WHEN age_at_loan < 30 THEN '<30'
            WHEN age_at_loan < 50 THEN '30-49'
            ELSE '50+' END AS age_band,
       COUNT(*) AS loans,
       ROUND(100.0 * AVG(is_bad::int), 2) AS bad_rate_pct
FROM analytics.v_loan_portfolio
GROUP BY duration, age_band
HAVING COUNT(*) >= 10
ORDER BY duration, age_band;

-- Q4. Saldo promedio de fin de mes por cuenta (CTE + DISTINCT ON), top 10
WITH month_end AS (
    SELECT DISTINCT ON (account_id, date_trunc('month', trans_date))
           account_id, date_trunc('month', trans_date)::date AS month, balance
    FROM core.trans
    ORDER BY account_id, date_trunc('month', trans_date), trans_date DESC, trans_id DESC
)
SELECT account_id, COUNT(*) AS months_active, ROUND(AVG(balance), 2) AS avg_month_end_balance
FROM month_end
GROUP BY account_id
ORDER BY avg_month_end_balance DESC
LIMIT 10;

-- Q5. Variación mensual del volumen de transacciones (LAG)
WITH monthly AS (
    SELECT date_trunc('month', trans_date)::date AS month,
           COUNT(*) AS n_trans,
           SUM(amount) FILTER (WHERE trans_type = 'CREDIT') AS credits
    FROM core.trans
    GROUP BY 1
)
SELECT month, n_trans,
       LAG(n_trans) OVER (ORDER BY month) AS prev_month,
       ROUND(100.0 * (n_trans - LAG(n_trans) OVER (ORDER BY month))
             / NULLIF(LAG(n_trans) OVER (ORDER BY month), 0), 2) AS pct_change
FROM monthly
ORDER BY month;

-- Q6. Desembolsos mensuales y acumulado (SUM OVER)
WITH monthly AS (
    SELECT date_trunc('month', loan_date)::date AS month,
           SUM(amount) AS disbursed
    FROM core.loan
    GROUP BY 1
)
SELECT month,
       disbursed,
       SUM(disbursed) OVER (ORDER BY month) AS cumulative
FROM monthly
ORDER BY month;

-- Q7. Top 3 distritos por monto prestado dentro de cada región (ROW_NUMBER)
WITH by_district AS (
    SELECT region, district_name, SUM(amount) AS total_amount
    FROM analytics.v_loan_portfolio
    GROUP BY region, district_name
), ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY region ORDER BY total_amount DESC) AS rn
    FROM by_district
)
SELECT region, district_name, total_amount, rn
FROM ranked WHERE rn <= 3
ORDER BY region, rn;

-- Q8. Saldo promedio de los 90 días previos al préstamo, por estado (LATERAL)
SELECT l.status,
       COUNT(*) AS loans,
       COUNT(pre.avg_balance) AS loans_with_history,
       ROUND(AVG(pre.avg_balance), 0) AS mean_balance,
       ROUND(percentile_cont(0.5) WITHIN GROUP (ORDER BY pre.avg_balance)::numeric, 0) AS median_balance
FROM core.loan l
JOIN LATERAL (
    SELECT AVG(t.balance) AS avg_balance
    FROM core.trans t
    WHERE t.account_id = l.account_id
      AND t.trans_date >= l.loan_date - INTERVAL '90 days'
      AND t.trans_date <  l.loan_date
) pre ON TRUE
GROUP BY l.status
ORDER BY l.status;