#!/usr/bin/env python3
from kubernetes import client, config, watch
import os, time, tempfile

def load_kube_from_env():
    """
    GitHub Actions 환경에서 kubeconfig 파일이 없으므로,
    환경변수(GITHUB_TOKEN, K8S_API_SERVER, K8S_CLUSTER_CA)를 이용해 동적으로 클러스터 연결 설정
    """
    api_server = os.getenv("K8S_API_SERVER")
    ca_cert_b64 = os.getenv("K8S_CLUSTER_CA")
    token = os.getenv("GITHUB_TOKEN")

    # CA 인증서 임시 파일 생성
    ca_file = tempfile.NamedTemporaryFile(delete=False)
    ca_file.write(bytes(ca_cert_b64, "utf-8"))
    ca_file.close()

    configuration = client.Configuration()
    configuration.host = api_server
    configuration.verify_ssl = True
    configuration.ssl_ca_cert = ca_file.name
    configuration.api_key = {"authorization": "Bearer " + token}
    client.Configuration.set_default(configuration)


def launch_pod(namespace="default"):
    load_kube_from_env()   # GitHub Actions 토큰 기반 인증
    v1 = client.CoreV1Api()

    # 기존 파드 삭제
    try:
        v1.delete_namespaced_pod(name="hello", namespace=namespace)
        time.sleep(1)
    except client.exceptions.ApiException as e:
        if e.status != 404:
            raise

    pod_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "hello"},
        "spec": {
            "containers": [{
                "name": "hello",
                "image": "busybox",
                "command": ["sh", "-c", "echo Hello world"],
            }],
            "restartPolicy": "Never"
        }
    }

    print("파드 생성")
    v1.create_namespaced_pod(namespace=namespace, body=pod_manifest)

    print("파드 생성 중")
    w = watch.Watch()
    for event in w.stream(v1.list_namespaced_pod, namespace=namespace, timeout_seconds=60):
        pod = event["object"]
        if pod.metadata.name == "hello" and pod.status.phase in ("Succeeded", "Failed"):
            print(f"파드 상태: {pod.status.phase}")
            w.stop()

    print("[Logs]:")
    logs = v1.read_namespaced_pod_log(name="hello", namespace=namespace, container="hello")
    print(logs.strip())

    v1.delete_namespaced_pod(name="hello", namespace=namespace)
    print("파드 삭제 완료")
    print("테스트")

if __name__ == "__main__":
    launch_pod()

