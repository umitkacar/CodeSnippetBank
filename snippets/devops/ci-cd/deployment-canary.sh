#!/bin/bash
# Canary deployment strategy for Kubernetes

set -e

NAMESPACE="${NAMESPACE:-production}"
APP_NAME="${APP_NAME:-myapp}"
NEW_IMAGE="${1}"
CANARY_PERCENTAGE="${2:-10}"

if [ -z "$NEW_IMAGE" ]; then
    echo "Usage: $0 <new-image> [canary-percentage]"
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
