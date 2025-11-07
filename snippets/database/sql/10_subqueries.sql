-- ============================================================================
-- SUBQUERIES - Scalar, Row, Table, and Correlated
-- ============================================================================

-- Snippet 1: Scalar subquery (single value)
SELECT
    product_id,
    product_name,
    price,
    price - (SELECT AVG(price) FROM products) AS price_vs_average
FROM products
WHERE is_active = true;

-- Snippet 2: Subquery in WHERE clause
SELECT
    customer_id,
    name,
    email
FROM customers
WHERE customer_id IN (
    SELECT DISTINCT customer_id
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
);

-- Snippet 3: Correlated subquery
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.price,
    (SELECT AVG(price)
     FROM products p2
     WHERE p2.category = p.category) AS category_avg_price
FROM products p
WHERE p.price > (
    SELECT AVG(price)
    FROM products p3
    WHERE p3.category = p.category
);

-- Snippet 4: EXISTS with correlated subquery
SELECT
    c.customer_id,
    c.name,
    c.email
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
        AND o.total_amount > 1000
        AND o.order_date >= CURRENT_DATE - INTERVAL '90 days'
);

-- Snippet 5: NOT EXISTS - Anti-join pattern
SELECT
    p.product_id,
    p.product_name,
    p.price
FROM products p
WHERE NOT EXISTS (
    SELECT 1
    FROM order_items oi
    WHERE oi.product_id = p.product_id
        AND oi.created_at >= CURRENT_DATE - INTERVAL '180 days'
)
AND p.is_active = true;

-- Snippet 6: Subquery in FROM clause (derived table)
SELECT
    dept_summary.department,
    dept_summary.employee_count,
    dept_summary.avg_salary,
    dept_summary.total_salary
FROM (
    SELECT
        department,
        COUNT(*) AS employee_count,
        AVG(salary) AS avg_salary,
        SUM(salary) AS total_salary
    FROM employees
    WHERE status = 'active'
    GROUP BY department
) AS dept_summary
WHERE dept_summary.avg_salary > 75000
ORDER BY dept_summary.total_salary DESC;

-- Snippet 7: Subquery with IN operator
SELECT
    order_id,
    customer_id,
    order_date,
    total_amount
FROM orders
WHERE customer_id IN (
    SELECT customer_id
    FROM customers
    WHERE segment = 'premium'
        AND status = 'active'
)
AND status = 'completed';

-- Snippet 8: Subquery with ALL operator
SELECT
    product_id,
    product_name,
    price
FROM products
WHERE price > ALL (
    SELECT price
    FROM products
    WHERE category = 'Budget'
)
AND category != 'Budget';

-- Snippet 9: Subquery with ANY/SOME operator
SELECT
    employee_id,
    name,
    salary,
    department
FROM employees e1
WHERE salary > ANY (
    SELECT AVG(salary)
    FROM employees e2
    WHERE e2.department != e1.department
    GROUP BY department
);

-- Snippet 10: Multiple column subquery
SELECT
    o.order_id,
    o.customer_id,
    o.order_date
FROM orders o
WHERE (o.customer_id, o.order_date) IN (
    SELECT customer_id, MAX(order_date)
    FROM orders
    GROUP BY customer_id
);

-- Snippet 11: Subquery with aggregate function
SELECT
    category,
    product_name,
    sales_count
FROM (
    SELECT
        p.category,
        p.product_name,
        COUNT(oi.order_item_id) AS sales_count,
        ROW_NUMBER() OVER (
            PARTITION BY p.category
            ORDER BY COUNT(oi.order_item_id) DESC
        ) AS rn
    FROM products p
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.category, p.product_name
) AS ranked_products
WHERE rn <= 5;

-- Snippet 12: Nested subqueries
SELECT
    customer_id,
    name,
    order_count
FROM customers
WHERE customer_id IN (
    SELECT customer_id
    FROM orders
    WHERE total_amount > (
        SELECT AVG(total_amount)
        FROM orders
        WHERE status = 'completed'
    )
    GROUP BY customer_id
    HAVING COUNT(*) >= 3
);

-- Snippet 13: Subquery with LATERAL join (PostgreSQL)
SELECT
    c.customer_id,
    c.name,
    recent_orders.order_id,
    recent_orders.order_date,
    recent_orders.total_amount
FROM customers c
CROSS JOIN LATERAL (
    SELECT order_id, order_date, total_amount
    FROM orders o
    WHERE o.customer_id = c.customer_id
    ORDER BY o.order_date DESC
    LIMIT 5
) AS recent_orders
WHERE c.status = 'active';

-- Snippet 14: Subquery for running calculations
SELECT
    o1.order_id,
    o1.order_date,
    o1.total_amount,
    (SELECT SUM(o2.total_amount)
     FROM orders o2
     WHERE o2.customer_id = o1.customer_id
         AND o2.order_date <= o1.order_date) AS running_customer_total
FROM orders o1
WHERE o1.customer_id = 123
ORDER BY o1.order_date;

-- Snippet 15: Complex correlated subquery with aggregation
SELECT
    e.employee_id,
    e.name,
    e.department,
    e.salary,
    (SELECT COUNT(*)
     FROM employees e2
     WHERE e2.department = e.department
         AND e2.salary >= e.salary) AS rank_in_department,
    (SELECT COUNT(*)
     FROM employees e3
     WHERE e3.manager_id = e.employee_id) AS direct_reports
FROM employees e
WHERE e.status = 'active'
ORDER BY e.department, rank_in_department;
