-- ============================================================================
-- INDEXING STRATEGIES - Advanced Index Optimization
-- ============================================================================

-- Snippet 1: Composite index column order matters
-- Rule: Most selective column first, or columns used in WHERE before ORDER BY

-- BEFORE (suboptimal):
CREATE INDEX idx_orders_date_status ON orders(order_date, status);

-- Query: WHERE status = 'pending' ORDER BY order_date
-- This index is less optimal for this query

-- AFTER (optimized):
CREATE INDEX idx_orders_status_date ON orders(status, order_date);
-- Better for: WHERE status = 'pending' ORDER BY order_date

-- Snippet 2: Partial indexes for specific conditions
-- Only index rows that match certain criteria
CREATE INDEX idx_active_users_email
ON users(email)
WHERE is_active = true AND deleted_at IS NULL;

-- Smaller index, faster queries for active users
SELECT * FROM users
WHERE email = 'user@example.com'
    AND is_active = true
    AND deleted_at IS NULL;

-- Snippet 3: Expression/functional indexes
-- Index computed values
CREATE INDEX idx_users_lower_email
ON users(LOWER(email));

-- Enables case-insensitive search
SELECT * FROM users
WHERE LOWER(email) = 'user@example.com';

-- Snippet 4: Full-text search indexes
-- GIN index for text search (PostgreSQL)
CREATE INDEX idx_products_fulltext
ON products
USING GIN(to_tsvector('english', name || ' ' || description));

-- Efficient full-text search
SELECT *
FROM products
WHERE to_tsvector('english', name || ' ' || description) @@
      to_tsquery('english', 'smartphone & camera');

-- Snippet 5: BRIN indexes for time-series data
-- Block Range INdex - very small, good for ordered data
CREATE INDEX idx_logs_created_brin
ON logs
USING BRIN(created_at);

-- Good for time-series queries
SELECT * FROM logs
WHERE created_at BETWEEN '2024-01-01' AND '2024-01-31';

-- Snippet 6: Covering indexes (INCLUDE clause)
-- Index contains all columns needed by query
CREATE INDEX idx_orders_customer_covering
ON orders(customer_id, order_date)
INCLUDE (total_amount, status);

-- Index-only scan possible (no table access needed)
SELECT customer_id, order_date, total_amount, status
FROM orders
WHERE customer_id = 123
    AND order_date >= '2024-01-01';

-- Snippet 7: Multi-column indexes for OR conditions
-- BEFORE (two separate index scans):
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_sku ON products(sku);

SELECT * FROM products
WHERE name = 'Widget' OR sku = 'WDG-001';

-- AFTER (single index scan with composite):
CREATE INDEX idx_products_name_sku ON products(name, sku);

-- Snippet 8: Unique partial index for soft deletes
CREATE UNIQUE INDEX idx_users_email_active
ON users(email)
WHERE deleted_at IS NULL;

-- Allows duplicate emails for deleted users
-- But enforces uniqueness for active users

-- Snippet 9: Index for JSON/JSONB queries (PostgreSQL)
-- GIN index for JSONB
CREATE INDEX idx_user_metadata_gin
ON users
USING GIN(metadata);

-- Query JSONB efficiently
SELECT * FROM users
WHERE metadata @> '{"subscription": "premium"}';

-- Index specific JSON path
CREATE INDEX idx_user_preferences_theme
ON users((metadata->>'theme'));

SELECT * FROM users
WHERE metadata->>'theme' = 'dark';

-- Snippet 10: Indexes for array operations (PostgreSQL)
CREATE INDEX idx_products_tags_gin
ON products
USING GIN(tags);

-- Efficient array containment queries
SELECT * FROM products
WHERE tags @> ARRAY['electronics', 'smartphone'];

-- Snippet 11: Conditional unique index
-- Enforce uniqueness only when certain conditions are met
CREATE UNIQUE INDEX idx_orders_invoice_number
ON orders(invoice_number)
WHERE invoice_number IS NOT NULL;

-- Snippet 12: Index for pattern matching
-- B-tree index with text_pattern_ops for LIKE queries
CREATE INDEX idx_products_name_pattern
ON products(name text_pattern_ops);

-- Enables index use for prefix searches
SELECT * FROM products
WHERE name LIKE 'Apple%';

-- For suffix or contains, use trigram index
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_products_name_trgm
ON products
USING GIN(name gin_trgm_ops);

SELECT * FROM products
WHERE name ILIKE '%phone%';

-- Snippet 13: Index maintenance queries

-- Find unused indexes
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS scans,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
    AND idx_scan = 0
    AND indexrelname NOT LIKE 'pg_toast%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Find duplicate indexes
SELECT
    a.indrelid::regclass AS table_name,
    a.indexrelid::regclass AS index1,
    b.indexrelid::regclass AS index2,
    a.indkey AS columns
FROM pg_index a
JOIN pg_index b ON a.indrelid = b.indrelid
    AND a.indkey = b.indkey
    AND a.indexrelid > b.indexrelid
WHERE a.indrelid::regclass::text NOT LIKE 'pg_%';

-- Find bloated indexes
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(indexrelid) DESC;

-- Snippet 14: Index for geospatial queries (PostGIS)
-- Install PostGIS extension first
CREATE EXTENSION IF NOT EXISTS postgis;

-- GIST index for spatial queries
CREATE INDEX idx_stores_location
ON stores
USING GIST(location);

-- Efficient spatial queries
SELECT *
FROM stores
WHERE ST_DWithin(
    location,
    ST_MakePoint(-73.935242, 40.730610)::geography,
    5000  -- 5km radius
);

-- Snippet 15: Optimize index builds
-- Create index concurrently (non-blocking)
CREATE INDEX CONCURRENTLY idx_large_table_column
ON large_table(column_name);

-- Drop index concurrently
DROP INDEX CONCURRENTLY IF EXISTS idx_old_index;

-- Snippet 16: Index for sorting with NULL handling
-- NULLS LAST optimization
CREATE INDEX idx_products_price_nulls_last
ON products(price DESC NULLS LAST);

SELECT *
FROM products
ORDER BY price DESC NULLS LAST
LIMIT 100;

-- Snippet 17: Multi-column index for range queries
-- Order matters: equality first, then range
CREATE INDEX idx_orders_status_date_range
ON orders(status, order_date);

-- Optimized for:
SELECT *
FROM orders
WHERE status = 'pending'
    AND order_date BETWEEN '2024-01-01' AND '2024-01-31';

-- Snippet 18: Index for complex WHERE conditions
-- Support multiple query patterns
CREATE INDEX idx_users_complex
ON users(country, city, created_at)
WHERE is_active = true;

-- Efficient for:
SELECT *
FROM users
WHERE country = 'US'
    AND city = 'New York'
    AND created_at >= '2024-01-01'
    AND is_active = true;

-- Snippet 19: Reindex for maintenance
-- Rebuild single index
REINDEX INDEX CONCURRENTLY idx_customers_email;

-- Rebuild all indexes on table
REINDEX TABLE CONCURRENTLY customers;

-- Rebuild all indexes in database
REINDEX DATABASE myapp;

-- Snippet 20: Monitor index effectiveness
-- Index hit ratio (should be > 99%)
SELECT
    sum(idx_blks_hit) / NULLIF(sum(idx_blks_hit + idx_blks_read), 0) * 100 AS index_hit_ratio
FROM pg_statio_user_indexes;

-- Table and index sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) -
                   pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
