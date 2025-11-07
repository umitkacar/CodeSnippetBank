-- ============================================================================
-- DATABASE TRIGGERS - Automated Actions
-- ============================================================================

-- Snippet 1: Before Insert Trigger - Set timestamps
CREATE OR REPLACE FUNCTION set_created_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.created_at = CURRENT_TIMESTAMP;
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_customers_set_created
    BEFORE INSERT ON customers
    FOR EACH ROW
    EXECUTE FUNCTION set_created_timestamp();

-- Snippet 2: Before Update Trigger - Update timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_customers_update_timestamp
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Snippet 3: After Insert Trigger - Create audit log
CREATE OR REPLACE FUNCTION log_new_customer()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO customer_audit_log (
        customer_id,
        action,
        action_timestamp,
        performed_by
    ) VALUES (
        NEW.customer_id,
        'CUSTOMER_CREATED',
        CURRENT_TIMESTAMP,
        current_user
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_customer_created
    AFTER INSERT ON customers
    FOR EACH ROW
    EXECUTE FUNCTION log_new_customer();

-- Snippet 4: Before Update Trigger - Prevent unauthorized changes
CREATE OR REPLACE FUNCTION prevent_price_decrease()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.price < OLD.price AND current_user != 'admin' THEN
        RAISE EXCEPTION 'Only admin can decrease prices';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_products_prevent_price_decrease
    BEFORE UPDATE ON products
    FOR EACH ROW
    WHEN (NEW.price IS DISTINCT FROM OLD.price)
    EXECUTE FUNCTION prevent_price_decrease();

-- Snippet 5: After Update Trigger - Track inventory changes
CREATE OR REPLACE FUNCTION track_inventory_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.stock_quantity != OLD.stock_quantity THEN
        INSERT INTO inventory_history (
            product_id,
            old_quantity,
            new_quantity,
            change_amount,
            change_timestamp,
            changed_by
        ) VALUES (
            NEW.product_id,
            OLD.stock_quantity,
            NEW.stock_quantity,
            NEW.stock_quantity - OLD.stock_quantity,
            CURRENT_TIMESTAMP,
            current_user
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_inventory_track_changes
    AFTER UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION track_inventory_changes();

-- Snippet 6: Before Delete Trigger - Soft delete
CREATE OR REPLACE FUNCTION soft_delete_customer()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE customers
    SET deleted_at = CURRENT_TIMESTAMP,
        status = 'deleted'
    WHERE customer_id = OLD.customer_id;
    RETURN NULL; -- Prevent actual delete
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_customer_soft_delete
    BEFORE DELETE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION soft_delete_customer();

-- Snippet 7: After Insert Trigger - Update denormalized data
CREATE OR REPLACE FUNCTION update_order_total()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE orders
    SET total_amount = (
        SELECT SUM(quantity * unit_price)
        FROM order_items
        WHERE order_id = NEW.order_id
    ),
    updated_at = CURRENT_TIMESTAMP
    WHERE order_id = NEW.order_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_items_update_total
    AFTER INSERT OR UPDATE OR DELETE ON order_items
    FOR EACH ROW
    EXECUTE FUNCTION update_order_total();

-- Snippet 8: Before Insert Trigger - Validate data
CREATE OR REPLACE FUNCTION validate_email()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        RAISE EXCEPTION 'Invalid email format: %', NEW.email;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_customers_validate_email
    BEFORE INSERT OR UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION validate_email();

-- Snippet 9: After Update Trigger - Send notifications
CREATE OR REPLACE FUNCTION notify_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status != OLD.status THEN
        INSERT INTO notifications (
            customer_id,
            notification_type,
            message,
            created_at
        ) VALUES (
            NEW.customer_id,
            'ORDER_STATUS_CHANGE',
            'Your order #' || NEW.order_id || ' status changed from ' ||
            OLD.status || ' to ' || NEW.status,
            CURRENT_TIMESTAMP
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_orders_notify_status
    AFTER UPDATE ON orders
    FOR EACH ROW
    WHEN (NEW.status IS DISTINCT FROM OLD.status)
    EXECUTE FUNCTION notify_status_change();

-- Snippet 10: Statement-level trigger
CREATE OR REPLACE FUNCTION log_bulk_operation()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO operation_log (
        table_name,
        operation_type,
        row_count,
        executed_at,
        executed_by
    ) VALUES (
        TG_TABLE_NAME,
        TG_OP,
        (SELECT COUNT(*) FROM NEW),
        CURRENT_TIMESTAMP,
        current_user
    );
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_products_log_bulk
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH STATEMENT
    EXECUTE FUNCTION log_bulk_operation();

-- Snippet 11: Complex trigger - Maintain referential integrity
CREATE OR REPLACE FUNCTION check_order_customer()
RETURNS TRIGGER AS $$
DECLARE
    v_customer_status VARCHAR;
BEGIN
    SELECT status INTO v_customer_status
    FROM customers
    WHERE customer_id = NEW.customer_id;

    IF v_customer_status IS NULL THEN
        RAISE EXCEPTION 'Customer % does not exist', NEW.customer_id;
    ELSIF v_customer_status = 'suspended' THEN
        RAISE EXCEPTION 'Cannot create order for suspended customer';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_orders_check_customer
    BEFORE INSERT ON orders
    FOR EACH ROW
    EXECUTE FUNCTION check_order_customer();

-- Snippet 12: Trigger with conditional execution
CREATE OR REPLACE FUNCTION archive_completed_orders()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND
       NEW.completed_at < CURRENT_DATE - INTERVAL '90 days' THEN
        INSERT INTO orders_archive
        SELECT * FROM orders WHERE order_id = NEW.order_id;
        DELETE FROM orders WHERE order_id = NEW.order_id;
        RETURN NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_orders_auto_archive
    AFTER UPDATE ON orders
    FOR EACH ROW
    WHEN (NEW.status = 'completed')
    EXECUTE FUNCTION archive_completed_orders();

-- Snippet 13: Disable/Enable triggers
ALTER TABLE customers DISABLE TRIGGER trg_customers_validate_email;
ALTER TABLE customers ENABLE TRIGGER trg_customers_validate_email;

-- Disable all triggers on a table
ALTER TABLE customers DISABLE TRIGGER ALL;
ALTER TABLE customers ENABLE TRIGGER ALL;

-- Snippet 14: Drop trigger
DROP TRIGGER IF EXISTS trg_customers_validate_email ON customers;

-- Snippet 15: List all triggers
SELECT
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement,
    action_timing
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;
