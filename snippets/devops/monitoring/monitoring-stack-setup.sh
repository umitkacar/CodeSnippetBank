#!/bin/bash
# Complete monitoring stack setup script

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Configuration
NAMESPACE="monitoring"
PROMETHEUS_VERSION="v2.48.0"
GRAFANA_VERSION="10.2.2"
ALERTMANAGER_VERSION="v0.26.0"

log_info "Setting up complete monitoring stack..."

# Create namespace
log_info "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Install Prometheus Operator
log_info "Installing Prometheus Operator..."
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

# Wait for operator to be ready
log_info "Waiting for Prometheus Operator..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=prometheus-operator -n default --timeout=300s

# Install kube-state-metrics
log_info "Installing kube-state-metrics..."
kubectl apply -f https://github.com/kubernetes/kube-state-metrics/releases/latest/download/kube-state-metrics.yaml

# Install node-exporter
log_info "Installing node-exporter..."
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: $NAMESPACE
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostNetwork: true
      hostPID: true
      containers:
      - name: node-exporter
        image: prom/node-exporter:latest
        args:
        - '--path.procfs=/host/proc'
        - '--path.sysfs=/host/sys'
        - '--path.rootfs=/host/root'
        ports:
        - containerPort: 9100
        volumeMounts:
        - name: proc
          mountPath: /host/proc
          readOnly: true
        - name: sys
          mountPath: /host/sys
          readOnly: true
        - name: root
          mountPath: /host/root
          readOnly: true
      volumes:
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
      - name: root
        hostPath:
          path: /
EOF

# Install Prometheus
log_info "Installing Prometheus..."
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: prometheus
  namespace: $NAMESPACE
spec:
  replicas: 2
  retention: 30d
  resources:
    requests:
      memory: 2Gi
      cpu: 1
    limits:
      memory: 4Gi
      cpu: 2
  serviceMonitorSelector:
    matchLabels:
      team: platform
  podMonitorSelector:
    matchLabels:
      team: platform
  ruleSelector:
    matchLabels:
      prometheus: main
EOF

# Install Grafana
log_info "Installing Grafana..."
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:$GRAFANA_VERSION
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: admin
        - name: GF_INSTALL_PLUGINS
          value: "grafana-piechart-panel"
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: $NAMESPACE
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
  type: LoadBalancer
EOF

# Install AlertManager
log_info "Installing AlertManager..."
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: Alertmanager
metadata:
  name: alertmanager
  namespace: $NAMESPACE
spec:
  replicas: 3
  resources:
    requests:
      memory: 256Mi
      cpu: 100m
EOF

# Install Loki
log_info "Installing Loki..."
kubectl apply -f https://raw.githubusercontent.com/grafana/loki/main/production/ksonnet/loki/loki.libsonnet

# Install Promtail
log_info "Installing Promtail..."
kubectl apply -f https://raw.githubusercontent.com/grafana/loki/main/production/ksonnet/promtail/promtail.libsonnet

# Verify installations
log_info "Verifying installations..."
kubectl get pods -n $NAMESPACE

log_info "Monitoring stack setup complete!"
log_info ""
log_info "Access Grafana:"
log_info "  kubectl port-forward -n $NAMESPACE svc/grafana 3000:3000"
log_info "  http://localhost:3000 (admin/admin)"
log_info ""
log_info "Access Prometheus:"
log_info "  kubectl port-forward -n $NAMESPACE svc/prometheus 9090:9090"
log_info "  http://localhost:9090"
