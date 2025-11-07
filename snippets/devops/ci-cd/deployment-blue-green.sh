#!/bin/bash
# Blue-Green deployment strategy for Kubernetes

set -e

NAMESPACE="${NAMESPACE:-production}"
APP_NAME="${APP_NAME:-myapp}"
NEW_IMAGE="${1}"
TIMEOUT=300

if [ -z "$NEW_IMAGE" ]; then
    echo "Usage: $0 <new-image>"
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
kubectl exec ${POD} -n ${NAMESPACE} -- curl -f http://localhost:8080/health || {
    echo "Smoke tests failed! Rolling back..."
    exit 1
}

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
