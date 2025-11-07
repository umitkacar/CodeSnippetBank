#!/bin/bash
# Rolling deployment strategy for Kubernetes

set -e

NAMESPACE="${NAMESPACE:-production}"
DEPLOYMENT="${1}"
IMAGE="${2}"
TIMEOUT=600

if [ -z "$DEPLOYMENT" ] || [ -z "$IMAGE" ]; then
    echo "Usage: $0 <deployment-name> <image>"
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
kubectl rollout status deployment/${DEPLOYMENT} \
    -n ${NAMESPACE} \
    --timeout=${TIMEOUT}s

# Verify deployment
echo
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
