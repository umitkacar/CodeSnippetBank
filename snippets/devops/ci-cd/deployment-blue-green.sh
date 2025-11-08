#!/bin/bash
# Blue-Green deployment strategy for Kubernetes
# Deploys new version to inactive environment, tests it, then switches traffic

set -euo pipefail  # Exit on error, undefined vars, and pipe failures
IFS=$'\n\t'  # Set safer internal field separator

NAMESPACE="${NAMESPACE:-production}"
APP_NAME="${APP_NAME:-myapp}"
NEW_IMAGE="${1:-}"
TIMEOUT=300

# Validate required arguments
if [ -z "$NEW_IMAGE" ]; then
    echo "ERROR: Missing required argument"
    echo "Usage: $0 <new-image>"
    echo ""
    echo "Example: $0 myregistry/myapp:v1.2.3"
    exit 1
fi

# Verify kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "ERROR: kubectl is not installed or not in PATH"
    exit 1
fi

# Verify service exists
if ! kubectl get service "${APP_NAME}" -n "${NAMESPACE}" &> /dev/null; then
    echo "ERROR: Service '${APP_NAME}' not found in namespace '${NAMESPACE}'"
    exit 1
fi

echo "=== Blue-Green Deployment ==="
echo "Namespace: $NAMESPACE"
echo "Application: $APP_NAME"
echo "New Image: $NEW_IMAGE"
echo

# Determine current active deployment
CURRENT=$(kubectl get service ${APP_NAME} -n ${NAMESPACE} -o jsonpath='{.spec.selector.version}')
echo "Current active version: $CURRENT"

# Determine new version
if [ "$CURRENT" = "blue" ]; then
    NEW="green"
    OLD="blue"
else
    NEW="blue"
    OLD="green"
fi

echo "Deploying to: $NEW"
echo

# Update the inactive deployment with new image
echo "Updating ${NEW} deployment..."
kubectl set image deployment/${APP_NAME}-${NEW} \
    ${APP_NAME}=${NEW_IMAGE} \
    -n ${NAMESPACE}

# Wait for rollout
echo "Waiting for ${NEW} deployment to be ready..."
kubectl rollout status deployment/${APP_NAME}-${NEW} -n ${NAMESPACE} --timeout=${TIMEOUT}s

# Run smoke tests
echo "Running smoke tests..."
POD=$(kubectl get pods -n ${NAMESPACE} -l app=${APP_NAME},version=${NEW} -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD" ]; then
    echo "ERROR: No pods found for version ${NEW}"
    echo "Cleaning up failed deployment..."
    kubectl scale deployment/${APP_NAME}-${NEW} --replicas=0 -n ${NAMESPACE}
    exit 1
fi

if ! kubectl exec ${POD} -n ${NAMESPACE} -- curl -f http://localhost:8080/health 2>/dev/null; then
    echo "ERROR: Smoke tests failed!"
    echo "Health check did not pass for new version"
    echo "Cleaning up failed deployment..."
    kubectl scale deployment/${APP_NAME}-${NEW} --replicas=0 -n ${NAMESPACE}
    exit 1
fi

echo "Smoke tests passed!"

# Switch traffic
echo "Switching traffic to ${NEW}..."
kubectl patch service ${APP_NAME} -n ${NAMESPACE} -p "{\"spec\":{\"selector\":{\"version\":\"${NEW}\"}}}"

echo "Waiting for service to update..."
sleep 10

# Verify service
echo "Verifying service..."
kubectl get service ${APP_NAME} -n ${NAMESPACE}

# Scale down old deployment
echo "Scaling down ${OLD} deployment..."
kubectl scale deployment/${APP_NAME}-${OLD} --replicas=0 -n ${NAMESPACE}

echo
echo "=== Deployment Complete ==="
echo "Active version: ${NEW}"
echo "To rollback, run: kubectl patch service ${APP_NAME} -n ${NAMESPACE} -p '{\"spec\":{\"selector\":{\"version\":\"${OLD}\"}}}'"
