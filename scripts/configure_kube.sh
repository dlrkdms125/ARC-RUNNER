#!/usr/bin/env bash
set -e

mkdir -p "$HOME/.kube"
echo "$K8S_CLUSTER_CA" | base64 --decode > "$HOME/.kube/ca.crt"

cat > "$HOME/.kube/config" <<EOF
apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority: "$HOME/.kube/ca.crt"
    server: $K8S_API_SERVER
  name: github-actions-cluster
contexts:
- context:
    cluster: github-actions-cluster
    user: github-actions
    namespace: $K8S_NAMESPACE
  name: github-actions-context
current-context: github-actions-context
users:
- name: github-actions
  user:
    token: $GITHUB_TOKEN
EOF
