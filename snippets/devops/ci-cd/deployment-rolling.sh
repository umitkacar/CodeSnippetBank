#!/bin/bash
# Rolling deployment strategy for Kubernetes
# Safely deploys a new version of an application with rolling updates

set -euo pipefail  # Exit on error, undefined vars, and pipe failures
IFS=$'\n\t'  # Set safer internal field separator

NAMESPACE="${NAMESPACE:-production}"
DEPLOYMENT="${1:-}"
IMAGE="${2:-}"
TIMEOUT=600

# Validate required arguments
if [ -z "$DEPLOYMENT" ] || [ -z "$IMAGE" ]; then
    echo "ERROR: Missing required arguments"
    echo "Usage: $0 <deployment-name> <image>"
    echo ""
    echo "Example: $0 myapp myregistry/myapp:v1.2.3"
    exit 1
fi

# Verify kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "ERROR: kubectl is not installed or not in PATH"
    exit 1
fi

# Verify deployment exists
if ! kubectl get deployment "${DEPLOYMENT}" -n "${NAMESPACE}" &> /dev/null; then
    echo "ERROR: Deployment '${DEPLOYMENT}' not found in namespace '${NAMESPACE}'"
    exit 1
fi

echo "=== Rolling Deployment ==="
echo "Namespace: $NAMESPACE"
echo "Deployment: $DEPLOYMENT"
echo "Image: $IMAGE"
echo

# Record deployment
kubectl annotate deployment/${DEPLOYMENT} \
    kubernetes.io/change-cause="Updated to ${IMAGE}" \
    -n ${NAMESPACE}

# Update deployment
echo "Updating deployment..."
kubectl set image deployment/${DEPLOYMENT} \
    *=${IMAGE} \
    -n ${NAMESPACE}

# Watch rollout
echo "Rolling out update..."
if ! kubectl rollout status deployment/${DEPLOYMENT} \
    -n ${NAMESPACE} \
    --timeout=${TIMEOUT}s; then
    echo ""
    echo "ERROR: Rollout failed or timed out!"
    echo "Rolling back to previous version..."
    kubectl rollout undo deployment/${DEPLOYMENT} -n ${NAMESPACE}
    echo "Rollback initiated. Check status with:"
    echo "  kubectl rollout status deployment/${DEPLOYMENT} -n ${NAMESPACE}"
    exit 1
fi

# Verify deployment
echo ""
echo "Verifying deployment..."
kubectl get deployment ${DEPLOYMENT} -n ${NAMESPACE}

# Show pod status
echo
echo "Pod status:"
kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT}

# Get rollout history
echo
echo "Rollout history:"
kubectl rollout history deployment/${DEPLOYMENT} -n ${NAMESPACE}

echo
echo "=== Deployment Complete ==="
echo
echo "To check logs:"
echo "  kubectl logs -f deployment/${DEPLOYMENT} -n ${NAMESPACE}"
echo
echo "To rollback:"
echo "  kubectl rollout undo deployment/${DEPLOYMENT} -n ${NAMESPACE}"
echo "  kubectl rollout undo deployment/${DEPLOYMENT} -n ${NAMESPACE} --to-revision=<revision>"
