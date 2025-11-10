#!/bin/bash
# Canary deployment strategy for Kubernetes
# Gradually rolls out new version to a percentage of traffic

set -euo pipefail  # Exit on error, undefined vars, and pipe failures
IFS=$'\n\t'  # Set safer internal field separator

NAMESPACE="${NAMESPACE:-production}"
APP_NAME="${APP_NAME:-myapp}"
NEW_IMAGE="${1:-}"
CANARY_PERCENTAGE="${2:-10}"

# Validate required arguments
if [ -z "$NEW_IMAGE" ]; then
    echo "ERROR: Missing required argument"
    echo "Usage: $0 <new-image> [canary-percentage]"
    echo ""
    echo "Example: $0 myregistry/myapp:v1.2.3 20"
    echo ""
    echo "Special commands:"
    echo "  $0 promote  - Promote canary to stable"
    echo "  $0 rollback - Rollback canary deployment"
    exit 1
fi

# Verify kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "ERROR: kubectl is not installed or not in PATH"
    exit 1
fi

# Validate canary percentage
if ! [[ "$CANARY_PERCENTAGE" =~ ^[0-9]+$ ]] || [ "$CANARY_PERCENTAGE" -lt 1 ] || [ "$CANARY_PERCENTAGE" -gt 100 ]; then
    echo "ERROR: Canary percentage must be between 1 and 100"
    exit 1
fi

echo "=== Canary Deployment ==="
echo "Namespace: $NAMESPACE"
echo "Application: $APP_NAME"
echo "New Image: $NEW_IMAGE"
echo "Canary Percentage: ${CANARY_PERCENTAGE}%"
echo

# Get current stable replicas
STABLE_REPLICAS=$(kubectl get deployment ${APP_NAME}-stable -n ${NAMESPACE} -o jsonpath='{.spec.replicas}')
TOTAL_REPLICAS=$((STABLE_REPLICAS + STABLE_REPLICAS / 10))

# Calculate canary replicas
CANARY_REPLICAS=$((TOTAL_REPLICAS * CANARY_PERCENTAGE / 100))
STABLE_REPLICAS=$((TOTAL_REPLICAS - CANARY_REPLICAS))

echo "Total replicas: $TOTAL_REPLICAS"
echo "Stable replicas: $STABLE_REPLICAS"
echo "Canary replicas: $CANARY_REPLICAS"
echo

# Update canary deployment
echo "Deploying canary version..."
kubectl set image deployment/${APP_NAME}-canary \
    ${APP_NAME}=${NEW_IMAGE} \
    -n ${NAMESPACE}

# Scale canary deployment
kubectl scale deployment/${APP_NAME}-canary \
    --replicas=${CANARY_REPLICAS} \
    -n ${NAMESPACE}

# Wait for canary rollout
echo "Waiting for canary deployment..."
kubectl rollout status deployment/${APP_NAME}-canary -n ${NAMESPACE}

echo
echo "=== Canary Deployed ==="
echo "Monitor metrics and errors. If stable, run:"
echo "  $0 promote"
echo "If issues occur, run:"
echo "  $0 rollback"
echo

# Promote function
promote_canary() {
    echo "=== Promoting Canary ==="

    # Update stable deployment
    kubectl set image deployment/${APP_NAME}-stable \
        ${APP_NAME}=${NEW_IMAGE} \
        -n ${NAMESPACE}

    # Wait for stable rollout
    kubectl rollout status deployment/${APP_NAME}-stable -n ${NAMESPACE}

    # Scale down canary
    kubectl scale deployment/${APP_NAME}-canary --replicas=0 -n ${NAMESPACE}

    echo "Promotion complete!"
}

# Rollback function
rollback_canary() {
    echo "=== Rolling Back Canary ==="

    # Scale down canary
    kubectl scale deployment/${APP_NAME}-canary --replicas=0 -n ${NAMESPACE}

    echo "Rollback complete!"
}

# Handle promote/rollback commands
if [ "$1" = "promote" ]; then
    promote_canary
elif [ "$1" = "rollback" ]; then
    rollback_canary
fi
