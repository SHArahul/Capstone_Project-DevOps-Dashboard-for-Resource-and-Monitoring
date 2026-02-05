-- Grafana AWS dashboard query --
-- 1. Estimated charges per day of services in aws cost (visualization time series: table format time series)
WITH daily AS (
  SELECT
    date,
    service_name,
    SUM(amortized_cost) AS daily_cost
  FROM aws_costs
  WHERE $__timeFilter(date)
  GROUP BY date, service_name
),
cumulative AS (
  SELECT
    date,
    service_name,
    SUM(daily_cost) OVER (
      PARTITION BY service_name, date_trunc('month', date)
      ORDER BY date
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cost_to_date,
    EXTRACT(DAY FROM date) AS elapsed_days
  FROM daily
)
SELECT
  date AS "time",
  service_name AS metric,
  ROUND(cost_to_date / NULLIF(elapsed_days, 0), 4) AS value
FROM cumulative
ORDER BY date;

-- 2. Estimated charges by AWS services (visualization time series)

SELECT
  date AS "time",
  service_name AS metric,
  SUM(amortized_cost) AS cost
FROM aws_costs
WHERE $__timeFilter(date)
GROUP BY date, service_name
ORDER BY date;


-- 3. total cost (amortized) in last calender month (visualization stat)

SELECT
  SUM(amortized_cost) AS total_cost_last_month
FROM aws_costs
WHERE date >= date_trunc('month', CURRENT_DATE - INTERVAL '1 month')
  AND date <  date_trunc('month', CURRENT_DATE);