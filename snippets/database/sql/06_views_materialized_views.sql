-- ============================================================================
-- VIEWS AND MATERIALIZED VIEWS - Database Abstractions
-- ============================================================================

-- Snippet 1: Simple view for security/abstraction
CREATE OR REPLACE VIEW customer_summary AS
SELECT
    customer_id,
    name,
    email,
    created_at,
    status
FROM customers
WHERE deleted_at IS NULL;

-- Snippet 2: View with aggregations
CREATE OR REPLACE VIEW monthly_sales_summary AS
SELECT
    DATE_TRUNC('month', order_date) AS month,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS avg_order_value
FROM orders
WHERE status = 'completed'
GROUP BY DATE_TRUNC('month', order_date);

-- Snippet 3: View with joins
CREATE OR REPLACE VIEW order_details AS
SELECT
    o.order_id,
    o.order_date,
    c.customer_id,
    c.name AS customer_name,
    c.email,
    p.product_id,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_total,
    o.status
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;

-- Snippet 4: Materialized view for performance
CREATE MATERIALIZED VIEW IF NOT EXISTS customer_lifetime_value AS
SELECT
    c.customer_id,
    c.name,
    c.email,
    c.created_at,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.total_amount) AS lifetime_value,
    AVG(o.total_amount) AS avg_order_value,
    MAX(o.order_date) AS last_order_date,
    MIN(o.order_date) AS first_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.status = 'active'
GROUP BY c.customer_id, c.name, c.email, c.created_at;

CREATE INDEX idx_mv_clv_customer ON customer_lifetime_value(customer_id);
CREATE INDEX idx_mv_clv_value ON customer_lifetime_value(lifetime_value DESC);

-- Snippet 5: Refresh materialized view
REFRESH MATERIALIZED VIEW customer_lifetime_value;

-- Concurrent refresh (PostgreSQL)
REFRESH MATERIALIZED VIEW CONCURRENTLY customer_lifetime_value;

-- Snippet 6: Materialized view with complex logic
CREATE MATERIALIZED VIEW IF NOT EXISTS product_performance_metrics AS
WITH daily_sales AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        DATE(o.order_date) AS sale_date,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM products p
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '365 days'
    GROUP BY p.product_id, p.product_name, p.category, DATE(o.order_date)
)
SELECT
    product_id,
    product_name,
    category,
    SUM(units_sold) AS total_units_sold,
    SUM(revenue) AS total_revenue,
    AVG(revenue) AS avg_daily_revenue,
    COUNT(DISTINCT sale_date) AS days_with_sales,
    MAX(sale_date) AS last_sale_date
FROM daily_sales
GROUP BY product_id, product_name, category;

CREATE UNIQUE INDEX idx_mv_product_perf ON product_performance_metrics(product_id);

-- Snippet 7: Updatable view (PostgreSQL)
CREATE OR REPLACE VIEW active_customers AS
SELECT
    customer_id,
    name,
    email,
    phone,
    status
FROM customers
WHERE status = 'active' AND deleted_at IS NULL;

-- Allow INSERT/UPDATE/DELETE on view
CREATE OR REPLACE RULE active_customers_update AS
ON UPDATE TO active_customers
DO INSTEAD
    UPDATE customers
    SET name = NEW.name,
        email = NEW.email,
        phone = NEW.phone,
        updated_at = CURRENT_TIMESTAMP
    WHERE customer_id = OLD.customer_id;

-- Snippet 8: View with window functions
CREATE OR REPLACE VIEW employee_rankings AS
SELECT
    employee_id,
    name,
    department,
    salary,
    hire_date,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS salary_rank,
    PERCENT_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS salary_percentile,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg_salary
FROM employees
WHERE status = 'active';

-- Snippet 9: Recursive view
CREATE OR REPLACE VIEW organization_hierarchy AS
WITH RECURSIVE emp_hierarchy AS (
    SELECT
        id,
        name,
        manager_id,
        title,
        1 AS level,
        ARRAY[id] AS path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    SELECT
        e.id,
        e.name,
        e.manager_id,
        e.title,
        eh.level + 1,
        eh.path || e.id
    FROM employees e
    JOIN emp_hierarchy eh ON e.manager_id = eh.id
)
SELECT * FROM emp_hierarchy;

-- Snippet 10: View with UNION
CREATE OR REPLACE VIEW all_transactions AS
SELECT
    'order' AS transaction_type,
    order_id AS transaction_id,
    customer_id,
    total_amount AS amount,
    order_date AS transaction_date
FROM orders
UNION ALL
SELECT
    'refund' AS transaction_type,
    refund_id AS transaction_id,
    customer_id,
    refund_amount AS amount,
    refund_date AS transaction_date
FROM refunds;

-- Snippet 11: Drop views
DROP VIEW IF EXISTS customer_summary CASCADE;
DROP MATERIALIZED VIEW IF EXISTS customer_lifetime_value;

-- Snippet 12: Check view definition
SELECT
    schemaname,
    viewname,
    definition
FROM pg_views
WHERE schemaname = 'public'
ORDER BY viewname;

-- Snippet 13: Materialized view with scheduled refresh (using cron or scheduler)
-- Create a function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY customer_lifetime_value;
    REFRESH MATERIALIZED VIEW CONCURRENTLY product_performance_metrics;
END;
$$ LANGUAGE plpgsql;

-- Schedule using pg_cron (if installed)
-- SELECT cron.schedule('refresh-mv', '0 2 * * *', 'SELECT refresh_materialized_views()');
