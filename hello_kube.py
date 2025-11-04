#!/usr/bin/env python3
from kubernetes import client, config, watch
import time

def launch_pod(namespace="default"):
    # kubeconfig 로드
    config.load_kube_config()
    v1 = client.CoreV1Api()

    # 기존 pod 있으면 삭제
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
                "command": ["echo", "Hello world"],  
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
    print(logs.strip())  #  정확히 "Hello world"만 출력

    v1.delete_namespaced_pod(name="hello", namespace=namespace)
    print("파드 삭제")

if __name__ == "__main__":
    launch_pod()

