-- ============================================================================
-- DATABASE INDEXES - Performance Optimization
-- ============================================================================

-- Snippet 1: Basic B-tree index (default)
CREATE INDEX idx_customers_email
ON customers(email);

-- Snippet 2: Unique index
CREATE UNIQUE INDEX idx_users_username
ON users(username);

-- Snippet 3: Composite index (multiple columns)
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date DESC);

-- Snippet 4: Partial index (filtered)
CREATE INDEX idx_active_products
ON products(product_name)
WHERE is_active = true AND deleted_at IS NULL;

-- Snippet 5: Expression index (function-based)
CREATE INDEX idx_users_lower_email
ON users(LOWER(email));

-- Snippet 6: Full-text search index (PostgreSQL)
CREATE INDEX idx_products_fulltext
ON products
USING GIN(to_tsvector('english', product_name || ' ' || description));

-- Snippet 7: JSONB index (PostgreSQL)
CREATE INDEX idx_user_metadata_gin
ON users
USING GIN(metadata);

-- For specific JSON path
CREATE INDEX idx_user_preferences
ON users
USING GIN((metadata->'preferences'));

-- Snippet 8: Covering index (include columns)
CREATE INDEX idx_orders_customer_covering
ON orders(customer_id, order_date)
INCLUDE (total_amount, status);

-- Snippet 9: Hash index (PostgreSQL - equality only)
CREATE INDEX idx_sessions_token_hash
ON sessions
USING HASH(session_token);

-- Snippet 10: Multi-column partial index
CREATE INDEX idx_orders_pending_customer
ON orders(customer_id, created_at)
WHERE status = 'pending';

-- Snippet 11: Descending index for ORDER BY optimization
CREATE INDEX idx_posts_created_desc
ON posts(created_at DESC, id DESC);

-- Snippet 12: GiST index for geometric/range data (PostgreSQL)
CREATE INDEX idx_events_daterange
ON events
USING GIST(date_range);

-- Snippet 13: Array index (PostgreSQL)
CREATE INDEX idx_posts_tags
ON posts
USING GIN(tags);

-- Snippet 14: Concurrent index creation (no locking)
CREATE INDEX CONCURRENTLY idx_large_table_column
ON large_table(column_name);

-- Snippet 15: Drop index
DROP INDEX IF EXISTS idx_old_index;

-- Snippet 16: Analyze index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC
LIMIT 20;

-- Snippet 17: Find unused indexes
SELECT
    schemaname || '.' || tablename AS table,
    indexname AS index,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan AS scans
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
    AND idx_scan = 0
    AND indexrelname NOT LIKE 'pg_toast%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Snippet 18: Check index bloat (PostgreSQL)
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(indexrelid) DESC;

-- Snippet 19: Reindex for maintenance
REINDEX INDEX CONCURRENTLY idx_customers_email;
REINDEX TABLE CONCURRENTLY customers;

-- Snippet 20: Bitmap index organization (for low cardinality)
-- Note: PostgreSQL uses bitmap scans automatically, Oracle has explicit bitmap indexes
CREATE INDEX idx_orders_status
ON orders(status)
WHERE status IN ('pending', 'processing', 'shipped');
