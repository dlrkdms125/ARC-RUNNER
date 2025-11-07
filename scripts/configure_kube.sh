#!/usr/bin/env bash
set -e

mkdir -p "$HOME/.kube"

# $K8S_CLUSTER_CA가 base64인지 PEM인지 자동 판단
if echo "$K8S_CLUSTER_CA" | grep -q "BEGIN CERTIFICATE"; then
  echo "$K8S_CLUSTER_CA" > "$HOME/.kube/ca.crt"
else
  echo "$K8S_CLUSTER_CA" | base64 --decode > "$HOME/.kube/ca.crt"
fi

cat > "$HOME/.kube/config" <<EOF
apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority-data: $(cat "$HOME/.kube/ca.crt" | base64 | tr -d '\n')
    server: ${K8S_API_SERVER}
  name: github-actions-cluster
contexts:
- context:
    cluster: github-actions-cluster
    user: github-actions
    namespace: ${K8S_NAMESPACE:-default}
  name: github-actions-context
current-context: github-actions-context
users:
- name: github-actions
  user:
    token: ${GITHUB_TOKEN}
EOF

chmod 600 "$HOME/.kube/config"

echo "✅ kubeconfig successfully created."
kubectl config view

