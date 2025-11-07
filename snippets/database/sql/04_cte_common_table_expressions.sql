-- ============================================================================
-- CTEs (Common Table Expressions) - Production Examples
-- ============================================================================

-- Snippet 1: Basic CTE for readability
WITH high_value_customers AS (
    SELECT
        customer_id,
        SUM(total_amount) AS lifetime_value
    FROM orders
    GROUP BY customer_id
    HAVING SUM(total_amount) > 10000
)
SELECT
    c.customer_id,
    c.name,
    c.email,
    hvc.lifetime_value
FROM customers c
INNER JOIN high_value_customers hvc ON c.customer_id = hvc.customer_id
ORDER BY hvc.lifetime_value DESC;

-- Snippet 2: Multiple CTEs
WITH
monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(total_amount) AS total_sales,
        COUNT(DISTINCT customer_id) AS unique_customers
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY DATE_TRUNC('month', order_date)
),
sales_with_growth AS (
    SELECT
        month,
        total_sales,
        unique_customers,
        LAG(total_sales) OVER (ORDER BY month) AS prev_month_sales,
        total_sales - LAG(total_sales) OVER (ORDER BY month) AS sales_growth
    FROM monthly_sales
)
SELECT
    month,
    total_sales,
    unique_customers,
    prev_month_sales,
    sales_growth,
    ROUND((sales_growth / NULLIF(prev_month_sales, 0) * 100)::numeric, 2) AS growth_pct
FROM sales_with_growth
ORDER BY month;

-- Snippet 3: Recursive CTE - Organization hierarchy
WITH RECURSIVE org_tree AS (
    -- Anchor: Top-level executives
    SELECT
        id,
        name,
        title,
        manager_id,
        1 AS level,
        name AS path,
        ARRAY[id] AS path_ids
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive: All subordinates
    SELECT
        e.id,
        e.name,
        e.title,
        e.manager_id,
        ot.level + 1,
        ot.path || ' -> ' || e.name,
        ot.path_ids || e.id
    FROM employees e
    INNER JOIN org_tree ot ON e.manager_id = ot.id
    WHERE NOT e.id = ANY(ot.path_ids) -- Prevent infinite loops
)
SELECT
    level,
    REPEAT('  ', level - 1) || name AS indented_name,
    title,
    path
FROM org_tree
ORDER BY path;

-- Snippet 4: Recursive CTE - Bill of materials
WITH RECURSIVE bom AS (
    -- Base: Final products
    SELECT
        product_id,
        product_name,
        component_id,
        quantity,
        1 AS level
    FROM product_components
    WHERE product_id = 'LAPTOP-X1'

    UNION ALL

    -- Recursive: Sub-components
    SELECT
        pc.product_id,
        pc.product_name,
        pc.component_id,
        pc.quantity * bom.quantity AS quantity,
        bom.level + 1
    FROM product_components pc
    INNER JOIN bom ON pc.product_id = bom.component_id
    WHERE bom.level < 10
)
SELECT
    level,
    REPEAT('  ', level - 1) || product_name AS component_hierarchy,
    component_id,
    SUM(quantity) AS total_quantity
FROM bom
GROUP BY level, product_name, component_id
ORDER BY level, product_name;

-- Snippet 5: CTE with aggregation and filtering
WITH
product_performance AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM products p
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY p.product_id, p.product_name, p.category
),
category_stats AS (
    SELECT
        category,
        AVG(revenue) AS avg_category_revenue
    FROM product_performance
    GROUP BY category
)
SELECT
    pp.product_id,
    pp.product_name,
    pp.category,
    pp.order_count,
    pp.units_sold,
    pp.revenue,
    cs.avg_category_revenue,
    pp.revenue - cs.avg_category_revenue AS revenue_vs_avg
FROM product_performance pp
JOIN category_stats cs ON pp.category = cs.category
WHERE pp.revenue > cs.avg_category_revenue
ORDER BY pp.revenue DESC;

-- Snippet 6: Recursive CTE - Date series generation
WITH RECURSIVE date_series AS (
    SELECT DATE '2024-01-01' AS date

    UNION ALL

    SELECT date + INTERVAL '1 day'
    FROM date_series
    WHERE date < DATE '2024-12-31'
)
SELECT
    ds.date,
    COALESCE(SUM(o.total_amount), 0) AS daily_revenue,
    COUNT(o.order_id) AS order_count
FROM date_series ds
LEFT JOIN orders o ON DATE(o.order_date) = ds.date
GROUP BY ds.date
ORDER BY ds.date;

-- Snippet 7: CTE for data deduplication
WITH ranked_records AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY email
            ORDER BY created_at DESC, id DESC
        ) AS rn
    FROM users
)
SELECT
    id,
    email,
    name,
    created_at
FROM ranked_records
WHERE rn = 1;

-- Snippet 8: CTE with window functions for percentile analysis
WITH
sales_with_percentile AS (
    SELECT
        salesperson_id,
        salesperson_name,
        total_sales,
        PERCENT_RANK() OVER (ORDER BY total_sales) AS percentile_rank,
        NTILE(10) OVER (ORDER BY total_sales) AS decile
    FROM salesperson_summary
    WHERE year = 2024
)
SELECT
    salesperson_id,
    salesperson_name,
    total_sales,
    ROUND((percentile_rank * 100)::numeric, 2) AS percentile,
    decile,
    CASE
        WHEN decile >= 9 THEN 'Top Performer'
        WHEN decile >= 7 THEN 'High Performer'
        WHEN decile >= 4 THEN 'Average Performer'
        ELSE 'Needs Improvement'
    END AS performance_category
FROM sales_with_percentile
ORDER BY total_sales DESC;

-- Snippet 9: Recursive CTE - Graph traversal
WITH RECURSIVE connected_nodes AS (
    -- Start node
    SELECT
        node_id,
        connected_to,
        1 AS distance,
        ARRAY[node_id] AS path
    FROM graph_edges
    WHERE node_id = 'START_NODE'

    UNION ALL

    -- Connected nodes
    SELECT
        ge.node_id,
        ge.connected_to,
        cn.distance + 1,
        cn.path || ge.node_id
    FROM graph_edges ge
    INNER JOIN connected_nodes cn ON ge.node_id = cn.connected_to
    WHERE NOT ge.node_id = ANY(cn.path)
        AND cn.distance < 10
)
SELECT DISTINCT
    connected_to AS reachable_node,
    MIN(distance) AS shortest_distance,
    (ARRAY_AGG(path ORDER BY distance))[1] AS shortest_path
FROM connected_nodes
GROUP BY connected_to
ORDER BY shortest_distance;

-- Snippet 10: Materialized CTE for performance (PostgreSQL)
WITH customer_metrics AS MATERIALIZED (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(total_amount) AS lifetime_value,
        AVG(total_amount) AS avg_order_value,
        MAX(order_date) AS last_order_date,
        MIN(order_date) AS first_order_date
    FROM orders
    WHERE order_date >= '2020-01-01'
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    c.name,
    c.segment,
    cm.order_count,
    cm.lifetime_value,
    cm.avg_order_value,
    CURRENT_DATE - cm.last_order_date AS days_since_last_order
FROM customers c
JOIN customer_metrics cm ON c.customer_id = cm.customer_id
WHERE cm.order_count >= 5
ORDER BY cm.lifetime_value DESC;
