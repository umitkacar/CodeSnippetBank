-- ============================================================================
-- SQL JOINS - All Types with Production Examples
-- ============================================================================

-- Snippet 1: INNER JOIN - Only matching records
SELECT
    c.customer_id,
    c.name AS customer_name,
    o.order_id,
    o.order_date,
    o.total_amount
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY o.order_date DESC;

-- Snippet 2: LEFT JOIN - All from left table
SELECT
    c.customer_id,
    c.name,
    c.email,
    COUNT(o.order_id) AS order_count,
    COALESCE(SUM(o.total_amount), 0) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email
ORDER BY total_spent DESC;

-- Snippet 3: RIGHT JOIN - All from right table
SELECT
    p.product_id,
    p.product_name,
    p.price,
    COALESCE(i.quantity_in_stock, 0) AS stock_quantity
FROM inventory i
RIGHT JOIN products p ON i.product_id = p.product_id
WHERE p.is_active = true;

-- Snippet 4: FULL OUTER JOIN - All from both tables
SELECT
    COALESCE(o.customer_id, r.customer_id) AS customer_id,
    o.order_id,
    o.total_amount,
    r.return_id,
    r.return_amount
FROM orders o
FULL OUTER JOIN returns r ON o.order_id = r.order_id
WHERE o.order_date >= '2024-01-01' OR r.return_date >= '2024-01-01';

-- Snippet 5: CROSS JOIN - Cartesian product
SELECT
    d.date,
    p.product_id,
    p.product_name,
    COALESCE(s.sales_quantity, 0) AS sales_quantity
FROM date_dimension d
CROSS JOIN products p
LEFT JOIN sales s ON d.date = s.sale_date AND p.product_id = s.product_id
WHERE d.date BETWEEN '2024-01-01' AND '2024-01-31'
    AND p.is_active = true;

-- Snippet 6: SELF JOIN - Compare within same table
SELECT
    e1.name AS employee,
    e1.title AS employee_title,
    e2.name AS manager,
    e2.title AS manager_title
FROM employees e1
LEFT JOIN employees e2 ON e1.manager_id = e2.id
WHERE e1.status = 'active'
ORDER BY e2.name, e1.name;

-- Snippet 7: Multiple JOINS
SELECT
    o.order_id,
    c.name AS customer_name,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_total,
    s.status AS shipment_status
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
LEFT JOIN shipments s ON o.order_id = s.order_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY o.order_id, oi.line_number;

-- Snippet 8: JOIN with aggregation
SELECT
    c.customer_id,
    c.name,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT p.product_id) AS unique_products,
    SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY c.customer_id, c.name
HAVING SUM(oi.quantity * oi.unit_price) > 10000
ORDER BY total_revenue DESC;

-- Snippet 9: LATERAL JOIN (PostgreSQL)
SELECT
    c.customer_id,
    c.name,
    recent.order_id,
    recent.order_date,
    recent.total_amount
FROM customers c
CROSS JOIN LATERAL (
    SELECT order_id, order_date, total_amount
    FROM orders o
    WHERE o.customer_id = c.customer_id
    ORDER BY o.order_date DESC
    LIMIT 3
) AS recent
WHERE c.status = 'active';

-- Snippet 10: Anti-join pattern (find non-matching records)
SELECT
    p.product_id,
    p.product_name,
    p.price
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE oi.product_id IS NULL
    AND p.is_active = true;

-- Snippet 11: JOIN with USING clause
SELECT
    o.order_id,
    o.total_amount,
    s.status,
    s.shipped_date
FROM orders o
INNER JOIN shipments s USING (order_id)
WHERE s.shipped_date >= CURRENT_DATE - INTERVAL '7 days';

-- Snippet 12: Complex JOIN with subquery
SELECT
    c.customer_id,
    c.name,
    c.email,
    top_products.product_list,
    top_products.total_spent
FROM customers c
INNER JOIN (
    SELECT
        o.customer_id,
        STRING_AGG(p.product_name, ', ' ORDER BY SUM(oi.quantity) DESC) AS product_list,
        SUM(oi.quantity * oi.unit_price) AS total_spent
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY o.customer_id
) AS top_products ON c.customer_id = top_products.customer_id
WHERE top_products.total_spent > 5000;
