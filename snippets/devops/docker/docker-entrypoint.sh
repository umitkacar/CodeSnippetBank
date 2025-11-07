#!/bin/bash
# Docker entrypoint script with initialization and graceful shutdown

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Wait for service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local timeout=${3:-30}
    local elapsed=0

    log_info "Waiting for $host:$port..."

    while ! nc -z "$host" "$port" 2>/dev/null; do
        if [ $elapsed -ge $timeout ]; then
            log_error "Timeout waiting for $host:$port"
            exit 1
        fi
        sleep 1
        elapsed=$((elapsed + 1))
    done

    log_info "$host:$port is ready"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."

    if [ -f "migrate.sh" ]; then
        ./migrate.sh
    elif command -v npm &> /dev/null && [ -f "package.json" ]; then
        npm run migrate
    else
        log_warn "No migration script found"
    fi
}

# Initialize application
initialize() {
    log_info "Initializing application..."

    # Wait for required services
    if [ -n "$DB_HOST" ]; then
        wait_for_service "$DB_HOST" "${DB_PORT:-5432}"
    fi

    if [ -n "$REDIS_HOST" ]; then
        wait_for_service "$REDIS_HOST" "${REDIS_PORT:-6379}"
    fi

    # Run migrations if enabled
    if [ "$RUN_MIGRATIONS" = "true" ]; then
        run_migrations
    fi

    # Seed data if needed
    if [ "$SEED_DATA" = "true" ]; then
        log_info "Seeding database..."
        npm run seed || log_warn "Seeding failed"
    fi

    log_info "Initialization complete"
}

# Graceful shutdown handler
shutdown() {
    log_info "Received shutdown signal, gracefully stopping..."

    # Send SIGTERM to child process
    if [ -n "$APP_PID" ]; then
        kill -TERM "$APP_PID" 2>/dev/null || true
        wait "$APP_PID"
    fi

    log_info "Shutdown complete"
    exit 0
}

# Trap signals for graceful shutdown
trap shutdown SIGTERM SIGINT SIGQUIT

# Initialize
initialize

# Start application
log_info "Starting application: $@"
exec "$@" &
APP_PID=$!

# Wait for application process
wait "$APP_PID"
