#!/bin/bash
# Docker container performance testing

set -e

CONTAINER="${1}"
DURATION="${2:-60}"

if [ -z "$CONTAINER" ]; then
    echo "Usage: $0 <container_name> [duration_seconds]"
    exit 1
fi

echo "=== Docker Container Performance Test ==="
echo "Container: $CONTAINER"
echo "Duration: ${DURATION}s"
echo

# Check if container exists
if ! docker ps | grep -q "$CONTAINER"; then
    echo "Error: Container $CONTAINER not found or not running"
    exit 1
fi

# Get container ID
CONTAINER_ID=$(docker ps -qf "name=$CONTAINER")

echo "--- Resource Usage ---"
docker stats --no-stream "$CONTAINER"

echo
echo "--- Network Stats ---"
docker exec "$CONTAINER" sh -c "cat /proc/net/dev" 2>/dev/null || echo "Cannot access network stats"

echo
echo "--- Disk I/O ---"
docker exec "$CONTAINER" sh -c "cat /proc/diskstats" 2>/dev/null || echo "Cannot access disk stats"

echo
echo "--- Running Performance Test (${DURATION}s) ---"

# Continuous monitoring
END=$((SECONDS+DURATION))
CSV_FILE="docker_perf_${CONTAINER}_$(date +%Y%m%d_%H%M%S).csv"

echo "timestamp,cpu_percent,memory_usage,memory_limit,memory_percent,net_input,net_output,block_input,block_output" > "$CSV_FILE"

while [ $SECONDS -lt $END ]; do
    docker stats --no-stream --format "{{.Container}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}}" "$CONTAINER" | \
    while IFS=',' read -r container cpu mem_usage mem_percent net block; do
        timestamp=$(date +%s)
        echo "$timestamp,$cpu,$mem_usage,$mem_percent,$net,$block" >> "$CSV_FILE"
    done
    sleep 1
done

echo
echo "Performance data saved to: $CSV_FILE"

echo
echo "--- Summary ---"
echo "Average CPU: $(awk -F',' 'NR>1 {sum+=$2; count++} END {print sum/count}' "$CSV_FILE")%"
echo "Peak Memory: $(sort -t',' -k3 -n "$CSV_FILE" | tail -1 | cut -d',' -f3)"
