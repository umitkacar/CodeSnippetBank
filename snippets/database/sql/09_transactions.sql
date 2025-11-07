-- ============================================================================
-- TRANSACTIONS - ACID Properties and Concurrency Control
-- ============================================================================

-- Snippet 1: Basic transaction
BEGIN;

UPDATE accounts
SET balance = balance - 100
WHERE account_id = 1;

UPDATE accounts
SET balance = balance + 100
WHERE account_id = 2;

COMMIT;

-- Snippet 2: Transaction with rollback
BEGIN;

INSERT INTO orders (customer_id, order_date, total_amount)
VALUES (123, CURRENT_TIMESTAMP, 500.00);

-- Check if customer has credit
DO $$
DECLARE
    v_credit_limit NUMERIC;
    v_current_balance NUMERIC;
BEGIN
    SELECT credit_limit, current_balance
    INTO v_credit_limit, v_current_balance
    FROM customers
    WHERE customer_id = 123;

    IF v_current_balance + 500 > v_credit_limit THEN
        RAISE EXCEPTION 'Credit limit exceeded';
    END IF;
END $$;

COMMIT;
-- If exception raised, transaction auto-rolls back

-- Snippet 3: Savepoint usage
BEGIN;

INSERT INTO orders (customer_id, order_date)
VALUES (123, CURRENT_TIMESTAMP);

SAVEPOINT order_created;

INSERT INTO order_items (order_id, product_id, quantity)
VALUES (CURRVAL('orders_order_id_seq'), 1, 5);

-- Something went wrong, rollback to savepoint
ROLLBACK TO SAVEPOINT order_created;

-- Try different items
INSERT INTO order_items (order_id, product_id, quantity)
VALUES (CURRVAL('orders_order_id_seq'), 2, 3);

COMMIT;

-- Snippet 4: Transaction isolation level - Read Committed (default)
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;

SELECT * FROM products WHERE product_id = 1;
-- Other transactions can modify this row
-- If we read again, we might see different data

COMMIT;

-- Snippet 5: Transaction isolation level - Repeatable Read
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;

SELECT * FROM products WHERE product_id = 1;
-- This row is now locked for this transaction
-- Reading again will show same data

SELECT * FROM products WHERE product_id = 1;
-- Same result as first SELECT

COMMIT;

-- Snippet 6: Transaction isolation level - Serializable
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

SELECT SUM(quantity) FROM inventory WHERE product_id = 1;

INSERT INTO orders (product_id, quantity)
VALUES (1, 10);

-- If another transaction modifies inventory for product 1,
-- this transaction will be rolled back on commit

COMMIT;

-- Snippet 7: Explicit locking - FOR UPDATE
BEGIN;

-- Lock rows for update
SELECT * FROM products
WHERE product_id = 1
FOR UPDATE;

-- Other transactions must wait
UPDATE products
SET stock_quantity = stock_quantity - 5
WHERE product_id = 1;

COMMIT;

-- Snippet 8: Explicit locking - FOR SHARE
BEGIN;

-- Allow other transactions to read but not modify
SELECT * FROM customers
WHERE customer_id = 123
FOR SHARE;

-- Read customer data safely
-- Other transactions can also read but not update

COMMIT;

-- Snippet 9: NOWAIT - Don't wait for locks
BEGIN;

SELECT * FROM products
WHERE product_id = 1
FOR UPDATE NOWAIT;
-- If locked, immediately raises error instead of waiting

UPDATE products
SET price = 99.99
WHERE product_id = 1;

COMMIT;

-- Snippet 10: SKIP LOCKED - Skip locked rows
BEGIN;

-- Process only unlocked orders
UPDATE orders
SET status = 'processing'
WHERE status = 'pending'
AND order_id IN (
    SELECT order_id
    FROM orders
    WHERE status = 'pending'
    ORDER BY created_at
    LIMIT 10
    FOR UPDATE SKIP LOCKED
)
RETURNING order_id;

COMMIT;

-- Snippet 11: Deferred constraints
BEGIN;

SET CONSTRAINTS ALL DEFERRED;

-- These might temporarily violate constraints
DELETE FROM order_items WHERE order_id = 100;
DELETE FROM orders WHERE order_id = 100;

-- Constraints checked at commit time
COMMIT;

-- Snippet 12: Two-phase commit preparation
BEGIN;

UPDATE accounts SET balance = balance - 1000 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 1000 WHERE account_id = 2;

-- Prepare transaction
PREPARE TRANSACTION 'transfer_001';

-- Later, either:
COMMIT PREPARED 'transfer_001';
-- Or:
-- ROLLBACK PREPARED 'transfer_001';

-- Snippet 13: Deadlock handling
DO $$
DECLARE
    v_retries INTEGER := 3;
    v_success BOOLEAN := FALSE;
BEGIN
    WHILE v_retries > 0 AND NOT v_success LOOP
        BEGIN
            -- Start transaction
            BEGIN;

            UPDATE accounts SET balance = balance - 100
            WHERE account_id = 1;

            UPDATE accounts SET balance = balance + 100
            WHERE account_id = 2;

            COMMIT;
            v_success := TRUE;

        EXCEPTION
            WHEN deadlock_detected THEN
                ROLLBACK;
                v_retries := v_retries - 1;
                IF v_retries > 0 THEN
                    RAISE NOTICE 'Deadlock detected, retrying... (% attempts left)', v_retries;
                    PERFORM pg_sleep(random() * 0.1); -- Random backoff
                ELSE
                    RAISE EXCEPTION 'Transaction failed after retries';
                END IF;
        END;
    END LOOP;
END $$;

-- Snippet 14: Advisory locks
-- Session-level advisory lock
SELECT pg_advisory_lock(123);
-- Critical section
SELECT pg_advisory_unlock(123);

-- Transaction-level advisory lock
BEGIN;
SELECT pg_advisory_xact_lock(456);
-- Lock automatically released on commit/rollback
COMMIT;

-- Try lock (non-blocking)
SELECT pg_try_advisory_lock(789);
-- Returns true if lock acquired, false otherwise

-- Snippet 15: Monitoring transactions
-- View current transactions
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    state_change,
    wait_event_type,
    wait_event,
    query
FROM pg_stat_activity
WHERE state != 'idle'
    AND pid != pg_backend_pid();

-- View blocking queries
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
