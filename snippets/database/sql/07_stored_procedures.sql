-- ============================================================================
-- STORED PROCEDURES AND FUNCTIONS - PostgreSQL
-- ============================================================================

-- Snippet 1: Simple stored procedure
CREATE OR REPLACE PROCEDURE update_customer_status(
    p_customer_id INTEGER,
    p_new_status VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE customers
    SET status = p_new_status,
        updated_at = CURRENT_TIMESTAMP
    WHERE customer_id = p_customer_id;

    COMMIT;
END;
$$;

-- Call: CALL update_customer_status(123, 'inactive');

-- Snippet 2: Function with return value
CREATE OR REPLACE FUNCTION calculate_order_total(p_order_id INTEGER)
RETURNS NUMERIC(10, 2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_total NUMERIC(10, 2);
BEGIN
    SELECT SUM(quantity * unit_price)
    INTO v_total
    FROM order_items
    WHERE order_id = p_order_id;

    RETURN COALESCE(v_total, 0);
END;
$$;

-- Usage: SELECT calculate_order_total(456);

-- Snippet 3: Procedure with error handling
CREATE OR REPLACE PROCEDURE process_order(
    p_customer_id INTEGER,
    p_product_ids INTEGER[],
    p_quantities INTEGER[],
    OUT p_order_id INTEGER,
    OUT p_success BOOLEAN,
    OUT p_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_product_id INTEGER;
    v_quantity INTEGER;
    v_price NUMERIC(10, 2);
    v_stock INTEGER;
    i INTEGER;
BEGIN
    p_success := false;

    -- Validate customer exists
    IF NOT EXISTS (SELECT 1 FROM customers WHERE customer_id = p_customer_id) THEN
        p_message := 'Customer not found';
        RETURN;
    END IF;

    -- Create order
    INSERT INTO orders (customer_id, order_date, status)
    VALUES (p_customer_id, CURRENT_TIMESTAMP, 'pending')
    RETURNING order_id INTO p_order_id;

    -- Process each item
    FOR i IN 1..array_length(p_product_ids, 1) LOOP
        v_product_id := p_product_ids[i];
        v_quantity := p_quantities[i];

        -- Check stock
        SELECT price, stock_quantity
        INTO v_price, v_stock
        FROM products
        WHERE product_id = v_product_id;

        IF v_stock < v_quantity THEN
            ROLLBACK;
            p_message := 'Insufficient stock for product ' || v_product_id;
            RETURN;
        END IF;

        -- Add order item
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        VALUES (p_order_id, v_product_id, v_quantity, v_price);

        -- Update stock
        UPDATE products
        SET stock_quantity = stock_quantity - v_quantity
        WHERE product_id = v_product_id;
    END LOOP;

    -- Update order total
    UPDATE orders
    SET total_amount = (
        SELECT SUM(quantity * unit_price)
        FROM order_items
        WHERE order_id = p_order_id
    )
    WHERE order_id = p_order_id;

    COMMIT;
    p_success := true;
    p_message := 'Order processed successfully';

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_success := false;
        p_message := 'Error: ' || SQLERRM;
END;
$$;

-- Snippet 4: Table-returning function
CREATE OR REPLACE FUNCTION get_customer_orders(p_customer_id INTEGER)
RETURNS TABLE (
    order_id INTEGER,
    order_date TIMESTAMP,
    total_amount NUMERIC(10, 2),
    status VARCHAR,
    item_count BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.order_id,
        o.order_date,
        o.total_amount,
        o.status,
        COUNT(oi.order_item_id) AS item_count
    FROM orders o
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.customer_id = p_customer_id
    GROUP BY o.order_id, o.order_date, o.total_amount, o.status
    ORDER BY o.order_date DESC;
END;
$$;

-- Usage: SELECT * FROM get_customer_orders(123);

-- Snippet 5: Function with default parameters
CREATE OR REPLACE FUNCTION search_products(
    p_search_term TEXT DEFAULT NULL,
    p_category VARCHAR DEFAULT NULL,
    p_min_price NUMERIC DEFAULT 0,
    p_max_price NUMERIC DEFAULT 999999,
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    product_id INTEGER,
    product_name VARCHAR,
    category VARCHAR,
    price NUMERIC,
    relevance REAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.price,
        ts_rank(
            to_tsvector('english', p.product_name || ' ' || p.description),
            plainto_tsquery('english', COALESCE(p_search_term, ''))
        ) AS relevance
    FROM products p
    WHERE (p_search_term IS NULL OR
           to_tsvector('english', p.product_name || ' ' || p.description) @@
           plainto_tsquery('english', p_search_term))
        AND (p_category IS NULL OR p.category = p_category)
        AND p.price BETWEEN p_min_price AND p_max_price
        AND p.is_active = true
    ORDER BY relevance DESC, p.product_name
    LIMIT p_limit;
END;
$$;

-- Snippet 6: Procedure with dynamic SQL
CREATE OR REPLACE PROCEDURE archive_old_records(
    p_table_name TEXT,
    p_date_column TEXT,
    p_days_old INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_archive_table TEXT;
    v_sql TEXT;
    v_count INTEGER;
BEGIN
    v_archive_table := p_table_name || '_archive';

    -- Create archive table if not exists
    v_sql := format(
        'CREATE TABLE IF NOT EXISTS %I (LIKE %I INCLUDING ALL)',
        v_archive_table, p_table_name
    );
    EXECUTE v_sql;

    -- Move old records
    v_sql := format(
        'WITH moved_rows AS (
            DELETE FROM %I
            WHERE %I < CURRENT_DATE - INTERVAL ''%s days''
            RETURNING *
        )
        INSERT INTO %I SELECT * FROM moved_rows',
        p_table_name, p_date_column, p_days_old, v_archive_table
    );

    EXECUTE v_sql;
    GET DIAGNOSTICS v_count = ROW_COUNT;

    RAISE NOTICE 'Archived % rows from % to %', v_count, p_table_name, v_archive_table;
    COMMIT;
END;
$$;

-- Snippet 7: Aggregate function
CREATE OR REPLACE FUNCTION array_median(numeric[])
RETURNS numeric
LANGUAGE plpgsql
AS $$
DECLARE
    v_sorted numeric[];
    v_count INTEGER;
BEGIN
    v_sorted := ARRAY(SELECT unnest($1) ORDER BY 1);
    v_count := array_length(v_sorted, 1);

    IF v_count = 0 THEN
        RETURN NULL;
    ELSIF v_count % 2 = 1 THEN
        RETURN v_sorted[(v_count + 1) / 2];
    ELSE
        RETURN (v_sorted[v_count / 2] + v_sorted[v_count / 2 + 1]) / 2.0;
    END IF;
END;
$$;

-- Snippet 8: Trigger function
CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

-- Snippet 9: Audit trigger function
CREATE OR REPLACE FUNCTION audit_changes()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, new_data, changed_by, changed_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW), current_user, CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, old_data, new_data, changed_by, changed_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW), current_user, CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, old_data, changed_by, changed_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), current_user, CURRENT_TIMESTAMP);
        RETURN OLD;
    END IF;
END;
$$;

-- Snippet 10: Batch processing procedure
CREATE OR REPLACE PROCEDURE batch_update_prices(
    p_category VARCHAR,
    p_increase_percent NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_batch_size INTEGER := 1000;
    v_updated INTEGER;
    v_total INTEGER := 0;
BEGIN
    LOOP
        WITH batch AS (
            SELECT product_id
            FROM products
            WHERE category = p_category
                AND NOT processed
            LIMIT v_batch_size
        )
        UPDATE products p
        SET price = price * (1 + p_increase_percent / 100),
            processed = true,
            updated_at = CURRENT_TIMESTAMP
        FROM batch b
        WHERE p.product_id = b.product_id;

        GET DIAGNOSTICS v_updated = ROW_COUNT;
        v_total := v_total + v_updated;

        EXIT WHEN v_updated = 0;

        RAISE NOTICE 'Processed % rows, total: %', v_updated, v_total;
        COMMIT;
    END LOOP;

    RAISE NOTICE 'Batch update complete. Total rows updated: %', v_total;
END;
$$;
