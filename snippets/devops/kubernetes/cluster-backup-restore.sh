#!/bin/bash
# Kubernetes cluster backup and restore

set -e

BACKUP_DIR="${BACKUP_DIR:-./k8s-backup}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$TIMESTAMP"

# Create backup directory
mkdir -p "$BACKUP_PATH"

echo "=== Kubernetes Cluster Backup ==="
echo "Backup location: $BACKUP_PATH"
echo

# Backup all namespaces
echo "Backing up namespaces..."
kubectl get namespaces -o yaml > "$BACKUP_PATH/namespaces.yaml"

# Get all namespaces
NAMESPACES=$(kubectl get namespaces -o jsonpath='{.items[*].metadata.name}')

# Backup resources from each namespace
for ns in $NAMESPACES; do
    echo "Backing up namespace: $ns"
    mkdir -p "$BACKUP_PATH/$ns"

    # Deployments
    kubectl get deployments -n "$ns" -o yaml > "$BACKUP_PATH/$ns/deployments.yaml" 2>/dev/null || true

    # StatefulSets
    kubectl get statefulsets -n "$ns" -o yaml > "$BACKUP_PATH/$ns/statefulsets.yaml" 2>/dev/null || true

    # DaemonSets
    kubectl get daemonsets -n "$ns" -o yaml > "$BACKUP_PATH/$ns/daemonsets.yaml" 2>/dev/null || true

    # Services
    kubectl get services -n "$ns" -o yaml > "$BACKUP_PATH/$ns/services.yaml" 2>/dev/null || true

    # ConfigMaps
    kubectl get configmaps -n "$ns" -o yaml > "$BACKUP_PATH/$ns/configmaps.yaml" 2>/dev/null || true

    # Secrets
    kubectl get secrets -n "$ns" -o yaml > "$BACKUP_PATH/$ns/secrets.yaml" 2>/dev/null || true

    # PVCs
    kubectl get pvc -n "$ns" -o yaml > "$BACKUP_PATH/$ns/pvcs.yaml" 2>/dev/null || true

    # Ingress
    kubectl get ingress -n "$ns" -o yaml > "$BACKUP_PATH/$ns/ingress.yaml" 2>/dev/null || true

    # Jobs
    kubectl get jobs -n "$ns" -o yaml > "$BACKUP_PATH/$ns/jobs.yaml" 2>/dev/null || true

    # CronJobs
    kubectl get cronjobs -n "$ns" -o yaml > "$BACKUP_PATH/$ns/cronjobs.yaml" 2>/dev/null || true
done

# Backup cluster-wide resources
echo "Backing up cluster-wide resources..."
mkdir -p "$BACKUP_PATH/cluster"

# PersistentVolumes
kubectl get pv -o yaml > "$BACKUP_PATH/cluster/pvs.yaml" 2>/dev/null || true

# StorageClasses
kubectl get storageclass -o yaml > "$BACKUP_PATH/cluster/storageclasses.yaml" 2>/dev/null || true

# ClusterRoles
kubectl get clusterroles -o yaml > "$BACKUP_PATH/cluster/clusterroles.yaml" 2>/dev/null || true

# ClusterRoleBindings
kubectl get clusterrolebindings -o yaml > "$BACKUP_PATH/cluster/clusterrolebindings.yaml" 2>/dev/null || true

# CustomResourceDefinitions
kubectl get crd -o yaml > "$BACKUP_PATH/cluster/crds.yaml" 2>/dev/null || true

# Nodes
kubectl get nodes -o yaml > "$BACKUP_PATH/cluster/nodes.yaml" 2>/dev/null || true

# Create tarball
echo "Creating backup archive..."
tar -czf "$BACKUP_DIR/k8s-backup-$TIMESTAMP.tar.gz" -C "$BACKUP_DIR" "$TIMESTAMP"

# Cleanup
rm -rf "$BACKUP_PATH"

echo
echo "Backup completed: $BACKUP_DIR/k8s-backup-$TIMESTAMP.tar.gz"
echo

# Restore function
restore_backup() {
    local backup_file=$1

    if [ ! -f "$backup_file" ]; then
        echo "Error: Backup file not found: $backup_file"
        exit 1
    fi

    echo "=== Kubernetes Cluster Restore ==="
    echo "Restoring from: $backup_file"
    echo

    # Extract backup
    local restore_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$restore_dir"

    # Find the backup directory
    local backup_content=$(ls -1 "$restore_dir" | head -1)
    local backup_path="$restore_dir/$backup_content"

    # Restore namespaces first
    echo "Restoring namespaces..."
    kubectl apply -f "$backup_path/namespaces.yaml"

    # Restore resources
    for ns_dir in "$backup_path"/*; do
        if [ -d "$ns_dir" ] && [ "$(basename "$ns_dir")" != "cluster" ]; then
            local ns=$(basename "$ns_dir")
            echo "Restoring namespace: $ns"

            for yaml_file in "$ns_dir"/*.yaml; do
                if [ -f "$yaml_file" ]; then
                    echo "  Applying $(basename "$yaml_file")"
                    kubectl apply -f "$yaml_file" -n "$ns" || true
                fi
            done
        fi
    done

    # Restore cluster-wide resources
    if [ -d "$backup_path/cluster" ]; then
        echo "Restoring cluster-wide resources..."
        for yaml_file in "$backup_path/cluster"/*.yaml; do
            if [ -f "$yaml_file" ]; then
                echo "  Applying $(basename "$yaml_file")"
                kubectl apply -f "$yaml_file" || true
            fi
        done
    fi

    # Cleanup
    rm -rf "$restore_dir"

    echo
    echo "Restore completed!"
}

# Usage information
if [ "$1" = "restore" ] && [ -n "$2" ]; then
    restore_backup "$2"
elif [ "$1" = "restore" ]; then
    echo "Usage: $0 restore <backup-file.tar.gz>"
    exit 1
fi
