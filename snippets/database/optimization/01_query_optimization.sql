-- ============================================================================
-- QUERY OPTIMIZATION - Performance Tuning Techniques
-- ============================================================================

-- Snippet 1: Use EXPLAIN ANALYZE to understand query performance
EXPLAIN ANALYZE
SELECT
    c.customer_id,
    c.name,
    COUNT(o.order_id) AS order_count,
    SUM(o.total_amount) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.created_at >= '2024-01-01'
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC
LIMIT 100;

-- Snippet 2: Optimize JOIN order - put most restrictive table first
-- BEFORE (slow):
SELECT *
FROM large_table lt
JOIN small_filtered_table sft ON lt.id = sft.id;

-- AFTER (optimized):
SELECT *
FROM small_filtered_table sft
JOIN large_table lt ON sft.id = lt.id;

-- Snippet 3: Use EXISTS instead of IN for subqueries
-- BEFORE (slower with large subquery results):
SELECT *
FROM customers
WHERE customer_id IN (
    SELECT DISTINCT customer_id
    FROM orders
    WHERE order_date >= '2024-01-01'
);

-- AFTER (optimized):
SELECT *
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
        AND o.order_date >= '2024-01-01'
);

-- Snippet 4: Avoid SELECT * - specify only needed columns
-- BEFORE:
SELECT *
FROM orders
WHERE status = 'pending';

-- AFTER (optimized):
SELECT
    order_id,
    customer_id,
    total_amount,
    created_at
FROM orders
WHERE status = 'pending';

-- Snippet 5: Use covering indexes to avoid table lookups
-- Create covering index:
CREATE INDEX idx_orders_covering
ON orders(status, created_at)
INCLUDE (order_id, customer_id, total_amount);

-- Query will use index-only scan:
SELECT order_id, customer_id, total_amount
FROM orders
WHERE status = 'pending'
    AND created_at >= CURRENT_DATE - INTERVAL '7 days';

-- Snippet 6: Optimize OR conditions with UNION
-- BEFORE (inefficient):
SELECT *
FROM products
WHERE category = 'Electronics'
    OR price > 1000;

-- AFTER (optimized if indexes exist on both columns):
SELECT *
FROM products
WHERE category = 'Electronics'
UNION
SELECT *
FROM products
WHERE price > 1000;

-- Snippet 7: Limit result set early with WHERE instead of HAVING
-- BEFORE (filters after aggregation):
SELECT
    category,
    COUNT(*) AS product_count
FROM products
GROUP BY category
HAVING category IN ('Electronics', 'Books');

-- AFTER (filters before aggregation):
SELECT
    category,
    COUNT(*) AS product_count
FROM products
WHERE category IN ('Electronics', 'Books')
GROUP BY category;

-- Snippet 8: Use indexed columns in WHERE clause
-- BEFORE (function on indexed column prevents index use):
SELECT *
FROM orders
WHERE DATE(order_date) = '2024-01-01';

-- AFTER (optimized to use index):
SELECT *
FROM orders
WHERE order_date >= '2024-01-01'
    AND order_date < '2024-01-02';

-- Snippet 9: Avoid wildcard at beginning of LIKE
-- BEFORE (cannot use index):
SELECT *
FROM products
WHERE name LIKE '%phone%';

-- AFTER (can use index):
SELECT *
FROM products
WHERE name LIKE 'phone%';

-- Or use full-text search:
SELECT *
FROM products
WHERE to_tsvector('english', name) @@ to_tsquery('english', 'phone');

-- Snippet 10: Optimize pagination with index
-- BEFORE (slow on large offsets):
SELECT *
FROM orders
ORDER BY created_at DESC
LIMIT 20 OFFSET 10000;

-- AFTER (cursor-based pagination):
SELECT *
FROM orders
WHERE created_at < '2024-01-01T12:00:00Z'
ORDER BY created_at DESC
LIMIT 20;

-- Snippet 11: Use materialized CTEs for complex calculations
-- BEFORE (CTE evaluated multiple times):
WITH customer_stats AS (
    SELECT
        customer_id,
        COUNT(*) AS order_count,
        SUM(total_amount) AS total_spent
    FROM orders
    GROUP BY customer_id
)
SELECT * FROM customer_stats WHERE order_count > 5
UNION ALL
SELECT * FROM customer_stats WHERE total_spent > 1000;

-- AFTER (PostgreSQL - materialized CTE):
WITH customer_stats AS MATERIALIZED (
    SELECT
        customer_id,
        COUNT(*) AS order_count,
        SUM(total_amount) AS total_spent
    FROM orders
    GROUP BY customer_id
)
SELECT * FROM customer_stats WHERE order_count > 5
UNION ALL
SELECT * FROM customer_stats WHERE total_spent > 1000;

-- Snippet 12: Batch updates instead of row-by-row
-- BEFORE (slow):
UPDATE products SET price = price * 1.1 WHERE id = 1;
UPDATE products SET price = price * 1.1 WHERE id = 2;
UPDATE products SET price = price * 1.1 WHERE id = 3;

-- AFTER (optimized):
UPDATE products
SET price = price * 1.1
WHERE id IN (1, 2, 3);

-- Snippet 13: Use LATERAL joins for correlated subqueries
-- BEFORE (correlated subquery):
SELECT
    c.customer_id,
    c.name,
    (SELECT MAX(order_date) FROM orders WHERE customer_id = c.customer_id) AS last_order
FROM customers c;

-- AFTER (optimized with LATERAL):
SELECT
    c.customer_id,
    c.name,
    lo.last_order
FROM customers c
CROSS JOIN LATERAL (
    SELECT MAX(order_date) AS last_order
    FROM orders
    WHERE customer_id = c.customer_id
) lo;

-- Snippet 14: Optimize COUNT queries
-- BEFORE (slow on large tables):
SELECT COUNT(*) FROM orders;

-- AFTER (approximate count, faster):
SELECT reltuples::bigint AS estimate
FROM pg_class
WHERE relname = 'orders';

-- Snippet 15: Use appropriate join types
-- BEFORE (unnecessary LEFT JOIN):
SELECT o.*, c.name
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.status = 'active';  -- This makes LEFT JOIN unnecessary

-- AFTER (optimized with INNER JOIN):
SELECT o.*, c.name
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
WHERE c.status = 'active';

-- Snippet 16: Avoid N+1 queries with proper joins
-- BEFORE (N+1 problem - one query per order):
SELECT * FROM orders;
-- Then for each order:
-- SELECT * FROM order_items WHERE order_id = ?;

-- AFTER (single query with join):
SELECT
    o.*,
    json_agg(oi.*) AS items
FROM orders o
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id;

-- Snippet 17: Use partial indexes for specific queries
CREATE INDEX idx_active_pending_orders
ON orders(created_at)
WHERE status = 'pending' AND is_active = true;

-- Query benefits from partial index:
SELECT *
FROM orders
WHERE status = 'pending'
    AND is_active = true
    AND created_at >= CURRENT_DATE - INTERVAL '7 days';

-- Snippet 18: Optimize aggregations with filtered indexes
CREATE INDEX idx_completed_orders_amount
ON orders(total_amount)
WHERE status = 'completed';

-- Query uses filtered index:
SELECT
    AVG(total_amount),
    MAX(total_amount),
    MIN(total_amount)
FROM orders
WHERE status = 'completed';

-- Snippet 19: Use window functions instead of self-joins
-- BEFORE (slow self-join):
SELECT
    o1.order_id,
    o1.total_amount,
    (SELECT SUM(o2.total_amount)
     FROM orders o2
     WHERE o2.customer_id = o1.customer_id
       AND o2.order_date <= o1.order_date) AS running_total
FROM orders o1;

-- AFTER (optimized with window function):
SELECT
    order_id,
    total_amount,
    SUM(total_amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
FROM orders;

-- Snippet 20: Optimize DISTINCT with GROUP BY
-- BEFORE:
SELECT DISTINCT customer_id
FROM orders
WHERE order_date >= '2024-01-01';

-- AFTER (can be faster with proper indexes):
SELECT customer_id
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY customer_id;
