-- ============================================================================
-- COMPLEX SQL QUERIES - Production Ready
-- ============================================================================

-- Query 1: Hierarchical data with recursive CTE
WITH RECURSIVE employee_hierarchy AS (
    -- Base case: top-level managers
    SELECT
        id,
        name,
        manager_id,
        title,
        1 AS level,
        CAST(name AS VARCHAR(1000)) AS path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: employees reporting to managers
    SELECT
        e.id,
        e.name,
        e.manager_id,
        e.title,
        eh.level + 1,
        CAST(eh.path || ' > ' || e.name AS VARCHAR(1000))
    FROM employees e
    INNER JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT * FROM employee_hierarchy
ORDER BY path;

-- Query 2: Find gaps in sequential data
SELECT
    t1.id + 1 AS gap_start,
    MIN(t2.id) - 1 AS gap_end
FROM orders t1
LEFT JOIN orders t2 ON t1.id < t2.id
WHERE NOT EXISTS (
    SELECT 1 FROM orders t3 WHERE t3.id = t1.id + 1
)
AND t2.id IS NOT NULL
GROUP BY t1.id
HAVING MIN(t2.id) - 1 > t1.id;

-- Query 3: Running calculations with self-join
SELECT
    o1.order_date,
    o1.amount,
    SUM(o2.amount) AS running_total,
    AVG(o2.amount) AS running_average
FROM orders o1
INNER JOIN orders o2 ON o2.order_date <= o1.order_date
GROUP BY o1.order_date, o1.amount
ORDER BY o1.order_date;

-- Query 4: Pivoting data dynamically
SELECT
    product_category,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 1 THEN amount ELSE 0 END) AS jan,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 2 THEN amount ELSE 0 END) AS feb,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 3 THEN amount ELSE 0 END) AS mar,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 4 THEN amount ELSE 0 END) AS apr,
    SUM(amount) AS total
FROM orders o
JOIN products p ON o.product_id = p.id
WHERE EXTRACT(YEAR FROM order_date) = 2024
GROUP BY product_category;

-- Query 5: Complex filtering with multiple conditions
SELECT
    c.customer_id,
    c.name,
    COUNT(DISTINCT o.id) AS order_count,
    SUM(o.total_amount) AS lifetime_value,
    MAX(o.order_date) AS last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.status = 'active'
    AND c.created_at >= CURRENT_DATE - INTERVAL '1 year'
    AND (
        o.total_amount > 1000
        OR EXISTS (
            SELECT 1 FROM order_items oi
            WHERE oi.order_id = o.id AND oi.quantity > 10
        )
    )
GROUP BY c.customer_id, c.name
HAVING COUNT(DISTINCT o.id) >= 3
ORDER BY lifetime_value DESC;

-- Query 6: Correlated subquery for ranking
SELECT
    e.name,
    e.department,
    e.salary,
    (SELECT COUNT(*)
     FROM employees e2
     WHERE e2.department = e.department
     AND e2.salary > e.salary) + 1 AS dept_rank
FROM employees e
WHERE e.status = 'active'
ORDER BY e.department, dept_rank;

-- Query 7: Multiple aggregations with GROUPING SETS
SELECT
    COALESCE(region, 'ALL REGIONS') AS region,
    COALESCE(product_category, 'ALL CATEGORIES') AS category,
    SUM(sales_amount) AS total_sales,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM sales
WHERE sale_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY GROUPING SETS (
    (region, product_category),
    (region),
    (product_category),
    ()
);

-- Query 8: Finding duplicates with all details
SELECT
    email,
    COUNT(*) AS duplicate_count,
    STRING_AGG(id::TEXT, ', ' ORDER BY created_at) AS duplicate_ids,
    MIN(created_at) AS first_created,
    MAX(created_at) AS last_created
FROM users
GROUP BY email
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;
