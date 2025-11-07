#!/bin/bash
# Useful kubectl commands and snippets

# Context and cluster management
kubectl config get-contexts
kubectl config use-context production
kubectl config current-context
kubectl cluster-info

# Namespace operations
kubectl create namespace production
kubectl get namespaces
kubectl config set-context --current --namespace=production

# Pod operations
kubectl get pods -A
kubectl get pods -n production -o wide
kubectl describe pod <pod-name>
kubectl logs <pod-name> -f
kubectl logs <pod-name> -c <container-name>
kubectl exec -it <pod-name> -- /bin/bash
kubectl port-forward <pod-name> 8080:80
kubectl top pods
kubectl delete pod <pod-name> --grace-period=0 --force

# Deployment operations
kubectl create deployment nginx --image=nginx:alpine
kubectl get deployments
kubectl describe deployment <deployment-name>
kubectl rollout status deployment/<deployment-name>
kubectl rollout history deployment/<deployment-name>
kubectl rollout undo deployment/<deployment-name>
kubectl rollout undo deployment/<deployment-name> --to-revision=2
kubectl scale deployment/<deployment-name> --replicas=5
kubectl set image deployment/<deployment-name> container=image:tag

# Service operations
kubectl expose deployment nginx --port=80 --type=LoadBalancer
kubectl get services
kubectl describe service <service-name>
kubectl get endpoints

# ConfigMap and Secret operations
kubectl create configmap app-config --from-file=config.properties
kubectl create configmap app-config --from-literal=key=value
kubectl get configmaps
kubectl describe configmap <configmap-name>
kubectl create secret generic db-secret --from-literal=password=mypassword
kubectl get secrets
kubectl describe secret <secret-name>

# Resource management
kubectl apply -f manifest.yaml
kubectl apply -f directory/
kubectl delete -f manifest.yaml
kubectl replace --force -f manifest.yaml
kubectl patch deployment nginx -p '{"spec":{"replicas":3}}'

# Debugging
kubectl describe pod <pod-name>
kubectl logs <pod-name> --previous
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl get pods --field-selector=status.phase=Failed
kubectl debug <pod-name> -it --image=busybox

# Resource usage
kubectl top nodes
kubectl top pods
kubectl top pods --containers

# YAML output and manipulation
kubectl get deployment nginx -o yaml
kubectl get deployment nginx -o json
kubectl get pods -o jsonpath='{.items[*].metadata.name}'
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase

# Labels and selectors
kubectl label pods <pod-name> environment=production
kubectl get pods -l environment=production
kubectl get pods -l 'environment in (production,staging)'

# Annotations
kubectl annotate pods <pod-name> description="My pod"
kubectl annotate pods <pod-name> description-

# Drain and cordon nodes
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
kubectl cordon <node-name>
kubectl uncordon <node-name>

# Taint nodes
kubectl taint nodes <node-name> key=value:NoSchedule
kubectl taint nodes <node-name> key=value:NoExecute
kubectl taint nodes <node-name> key-

# Certificate management
kubectl get csr
kubectl certificate approve <csr-name>
kubectl certificate deny <csr-name>

# API resources
kubectl api-resources
kubectl api-versions
kubectl explain pods
kubectl explain pods.spec.containers

# Diff before apply
kubectl diff -f manifest.yaml

# Wait for condition
kubectl wait --for=condition=ready pod/<pod-name>
kubectl wait --for=condition=available --timeout=600s deployment/<deployment-name>

# Copy files
kubectl cp <pod-name>:/path/to/file /local/path
kubectl cp /local/path <pod-name>:/path/to/file

# Auth can-i
kubectl auth can-i create deployments
kubectl auth can-i delete nodes
kubectl auth can-i create pods --as=user@example.com

# Resource cleanup
kubectl delete pod --field-selector=status.phase==Failed
kubectl delete pod --field-selector=status.phase==Succeeded

# Quick pod for debugging
kubectl run debug --rm -it --image=alpine -- sh
kubectl run curl --rm -it --image=curlimages/curl -- sh

# Get resource usage
kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes
kubectl get --raw /apis/metrics.k8s.io/v1beta1/pods
