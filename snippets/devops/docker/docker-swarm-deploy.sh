#!/bin/bash
# Docker Swarm deployment script

set -e

STACK_NAME="${1:-myapp}"
COMPOSE_FILE="${2:-docker-compose.yml}"
ENV_FILE="${3:-.env}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Docker Swarm Deployment ===${NC}"

# Check if swarm is initialized
if ! docker info | grep -q "Swarm: active"; then
    echo "Initializing Docker Swarm..."
    docker swarm init
fi

# Load environment variables
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment from $ENV_FILE"
    export $(cat $ENV_FILE | grep -v '^#' | xargs)
fi

# Create secrets
create_secrets() {
    echo "Creating secrets..."

    if [ -n "$DB_PASSWORD" ]; then
        echo "$DB_PASSWORD" | docker secret create db_password - 2>/dev/null || echo "Secret db_password already exists"
    fi

    if [ -n "$API_KEY" ]; then
        echo "$API_KEY" | docker secret create api_key - 2>/dev/null || echo "Secret api_key already exists"
    fi
}

# Create configs
create_configs() {
    echo "Creating configs..."

    if [ -f "nginx.conf" ]; then
        docker config create nginx_config nginx.conf 2>/dev/null || echo "Config nginx_config already exists"
    fi
}

# Deploy stack
deploy_stack() {
    echo -e "${GREEN}Deploying stack: $STACK_NAME${NC}"

    docker stack deploy \
        --compose-file $COMPOSE_FILE \
        --prune \
        --resolve-image always \
        $STACK_NAME

    echo "Waiting for services to stabilize..."
    sleep 10
}

# Show service status
show_status() {
    echo -e "\n${GREEN}=== Service Status ===${NC}"
    docker stack services $STACK_NAME

    echo -e "\n${GREEN}=== Service Tasks ===${NC}"
    docker stack ps $STACK_NAME --no-trunc
}

# Monitor deployment
monitor_deployment() {
    echo -e "\n${GREEN}Monitoring deployment...${NC}"

    local timeout=300
    local elapsed=0

    while [ $elapsed -lt $timeout ]; do
        local converged=$(docker stack ps $STACK_NAME --format "{{.CurrentState}}" | grep -c "Running" || true)
        local total=$(docker stack ps $STACK_NAME --format "{{.CurrentState}}" | wc -l)

        if [ $converged -eq $total ]; then
            echo -e "${GREEN}Deployment successful!${NC}"
            return 0
        fi

        echo "Progress: $converged/$total tasks running..."
        sleep 5
        elapsed=$((elapsed + 5))
    done

    echo -e "${YELLOW}Deployment timeout!${NC}"
    return 1
}

# Main execution
create_secrets
create_configs
deploy_stack
show_status
monitor_deployment

echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
echo "View logs: docker service logs ${STACK_NAME}_app -f"
echo "Scale service: docker service scale ${STACK_NAME}_app=5"
echo "Remove stack: docker stack rm ${STACK_NAME}"
