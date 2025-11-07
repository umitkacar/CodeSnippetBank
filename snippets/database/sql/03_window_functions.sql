-- ============================================================================
-- WINDOW FUNCTIONS - Advanced Analytics
-- ============================================================================

-- Snippet 1: ROW_NUMBER - Unique row numbering
SELECT
    product_id,
    product_name,
    category,
    price,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) AS price_rank
FROM products
WHERE is_active = true;

-- Snippet 2: RANK and DENSE_RANK - Handle ties differently
SELECT
    employee_id,
    name,
    department,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rank
FROM employees
WHERE status = 'active';

-- Snippet 3: NTILE - Divide into buckets
SELECT
    customer_id,
    name,
    total_purchases,
    NTILE(4) OVER (ORDER BY total_purchases DESC) AS quartile,
    CASE NTILE(4) OVER (ORDER BY total_purchases DESC)
        WHEN 1 THEN 'Top Tier'
        WHEN 2 THEN 'High Value'
        WHEN 3 THEN 'Medium Value'
        WHEN 4 THEN 'Low Value'
    END AS customer_segment
FROM customer_summary;

-- Snippet 4: Running totals with SUM window function
SELECT
    order_date,
    order_id,
    amount,
    SUM(amount) OVER (ORDER BY order_date, order_id) AS running_total,
    SUM(amount) OVER (
        ORDER BY order_date, order_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_sum
FROM orders
WHERE order_date >= '2024-01-01';

-- Snippet 5: Moving average
SELECT
    date,
    sales_amount,
    AVG(sales_amount) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7_days,
    AVG(sales_amount) OVER (
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS moving_avg_30_days
FROM daily_sales
ORDER BY date;

-- Snippet 6: LAG and LEAD - Access previous/next rows
SELECT
    date,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY date) AS previous_day_revenue,
    LEAD(revenue, 1) OVER (ORDER BY date) AS next_day_revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY date) AS day_over_day_change,
    ROUND(
        ((revenue - LAG(revenue, 1) OVER (ORDER BY date)) /
         NULLIF(LAG(revenue, 1) OVER (ORDER BY date), 0) * 100)::numeric,
        2
    ) AS pct_change
FROM daily_revenue
WHERE date >= CURRENT_DATE - INTERVAL '30 days';

-- Snippet 7: FIRST_VALUE and LAST_VALUE
SELECT
    employee_id,
    name,
    department,
    hire_date,
    salary,
    FIRST_VALUE(salary) OVER (
        PARTITION BY department
        ORDER BY hire_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS first_hire_salary,
    LAST_VALUE(salary) OVER (
        PARTITION BY department
        ORDER BY hire_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS latest_hire_salary
FROM employees;

-- Snippet 8: Percentile calculations
SELECT
    product_id,
    product_name,
    price,
    PERCENT_RANK() OVER (ORDER BY price) AS percent_rank,
    CUME_DIST() OVER (ORDER BY price) AS cumulative_distribution,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) OVER () AS median_price
FROM products
WHERE is_active = true;

-- Snippet 9: Complex window with multiple partitions
SELECT
    sale_date,
    region,
    product_category,
    sales_amount,
    SUM(sales_amount) OVER (
        PARTITION BY region, product_category
        ORDER BY sale_date
    ) AS category_region_running_total,
    AVG(sales_amount) OVER (
        PARTITION BY region
        ORDER BY sale_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS region_7day_avg,
    RANK() OVER (
        PARTITION BY region, DATE_TRUNC('month', sale_date)
        ORDER BY sales_amount DESC
    ) AS monthly_rank_in_region
FROM sales
WHERE sale_date >= '2024-01-01';

-- Snippet 10: Window functions with FILTER clause (PostgreSQL)
SELECT
    department,
    COUNT(*) AS total_employees,
    COUNT(*) FILTER (WHERE gender = 'F') AS female_count,
    COUNT(*) FILTER (WHERE gender = 'M') AS male_count,
    AVG(salary) AS avg_salary,
    AVG(salary) FILTER (WHERE years_experience > 5) AS avg_salary_experienced,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) AS median_salary
FROM employees
GROUP BY department;

-- Snippet 11: Gap and island problem using window functions
WITH numbered_sequences AS (
    SELECT
        id,
        value,
        date,
        ROW_NUMBER() OVER (ORDER BY date) AS rn,
        date - (ROW_NUMBER() OVER (ORDER BY date) * INTERVAL '1 day') AS island_id
    FROM events
    WHERE event_type = 'active'
)
SELECT
    MIN(date) AS island_start,
    MAX(date) AS island_end,
    COUNT(*) AS consecutive_days
FROM numbered_sequences
GROUP BY island_id
ORDER BY island_start;

-- Snippet 12: Year-over-year comparison with window functions
SELECT
    DATE_TRUNC('month', sale_date) AS month,
    SUM(amount) AS current_year_sales,
    LAG(SUM(amount), 12) OVER (ORDER BY DATE_TRUNC('month', sale_date)) AS previous_year_sales,
    SUM(amount) - LAG(SUM(amount), 12) OVER (ORDER BY DATE_TRUNC('month', sale_date)) AS yoy_change,
    ROUND(
        ((SUM(amount) - LAG(SUM(amount), 12) OVER (ORDER BY DATE_TRUNC('month', sale_date))) /
         NULLIF(LAG(SUM(amount), 12) OVER (ORDER BY DATE_TRUNC('month', sale_date)), 0) * 100)::numeric,
        2
    ) AS yoy_pct_change
FROM sales
GROUP BY DATE_TRUNC('month', sale_date)
ORDER BY month;
