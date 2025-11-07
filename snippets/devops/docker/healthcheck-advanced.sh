#!/bin/bash
# Advanced health check script for Docker containers

set -e

# Configuration
SERVICE_URL="${SERVICE_URL:-http://localhost:8080}"
HEALTH_ENDPOINT="${HEALTH_ENDPOINT:-/health}"
MAX_RETRIES=3
TIMEOUT=5

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local expected_status=${2:-200}

    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null)

    if [ "$response" = "$expected_status" ]; then
        return 0
    else
        return 1
    fi
}

# Function to check database connection
check_database() {
    local db_type=$1

    case $db_type in
        postgres)
            pg_isready -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U ${DB_USER:-postgres} > /dev/null 2>&1
            ;;
        mysql)
            mysqladmin ping -h ${DB_HOST:-localhost} -P ${DB_PORT:-3306} > /dev/null 2>&1
            ;;
        mongodb)
            mongosh --host ${DB_HOST:-localhost} --port ${DB_PORT:-27017} --eval "db.adminCommand('ping')" > /dev/null 2>&1
            ;;
        redis)
            redis-cli -h ${DB_HOST:-localhost} -p ${DB_PORT:-6379} ping > /dev/null 2>&1
            ;;
    esac
}

# Function to check disk space
check_disk_space() {
    local threshold=${1:-90}
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

    if [ "$usage" -lt "$threshold" ]; then
        return 0
    else
        echo "Disk usage is ${usage}%, threshold is ${threshold}%"
        return 1
    fi
}

# Function to check memory usage
check_memory() {
    local threshold=${1:-90}
    local usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')

    if [ "$usage" -lt "$threshold" ]; then
        return 0
    else
        echo "Memory usage is ${usage}%, threshold is ${threshold}%"
        return 1
    fi
}

# Main health check
main() {
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        # Check HTTP endpoint
        if check_http "${SERVICE_URL}${HEALTH_ENDPOINT}"; then
            # Optional: Check database
            if [ -n "$DB_TYPE" ]; then
                if ! check_database "$DB_TYPE"; then
                    echo "Database check failed"
                    retries=$((retries + 1))
                    sleep 1
                    continue
                fi
            fi

            # Optional: Check resources
            if ! check_disk_space 90; then
                echo "Disk space check failed"
                exit 1
            fi

            if ! check_memory 90; then
                echo "Memory check failed"
                exit 1
            fi

            echo "Health check passed"
            exit 0
        fi

        retries=$((retries + 1))
        sleep 1
    done

    echo "Health check failed after $MAX_RETRIES retries"
    exit 1
}

main
