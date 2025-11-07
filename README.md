## Github Actions Self-hosted Runner를 쿠버네티스 클러스터 위에 올리고, ARC를 이용해서 쿠버네티스 API를 호출하는 hello-kube CLI 앱을 빌드 및 실행하는 전체 파이프라인 만들기

### 실행환경
| 구성요소 | 버전 / 환경 |
| --- | --- |
| **OS** | Ubuntu 22.04 (GCP VM 위에 설치) |
| **Kubernetes Cluster** | Minikube (v1.34 이상) |
| **Container Runtime** | Docker |
| **Python** | 3.11 (kubernetes Python SDK 사용) |
| **kubectl** | v1.30 이상 |
| **Helm** | 3.x |
| **ArgoCD** | v2.x (Helm으로 설치) |
| **GitHub Actions** | CI/CD 실행 환경 |
| **DockerHub** | 컨테이너 이미지 저장소 |
### 프로젝트 구조
<img width="356" height="338" alt="image" src="https://github.com/user-attachments/assets/4a50712c-b597-46ed-bcb5-19bd71a36f7a" />


### 실행 방법
1. 사전 준비  
   1. GCP VM 생성 및 쿠버네티스 설치  
    1-1) ubuntu 22.04  
    1-2) VM 내의 도커 컨테이너에 minikube로 쿠버네티스 클러스터 생성    
     `minikube start --driver=docker --cpus=4 --memory=4f`
    1-3) kubectl 설치
   2. hello-kube 쿠버네티스 API/SDK로 hello라는 파드 생성
   3. github actions runner controller(ARC) 설치  
      3-1) helm으로 설치 준비  
      `helm repo add actions-runner-controller https://actions-runner-controller.github.io/actions-runner-controller`
      3-2) GitApp 셍성  
      App을 레포지토리에 추가하고 Client ID, Client Secret, Private Key 생성  
      3-3) values.yaml 파일 작성  
      `helm upgrade --install github-arc actions-runner-controller/gha-runner-scale-set-controller \
-f values.yaml -n arc --create-namespace`
    4. github actions이 hello pod 실행  
       4-1) configure_kube.sh를 통해 kubeconfig 생성  
       4-2) Github token으로 인증  
       4-3) hello.yaml을 클러스터에 적용  
   5. docker 이미지 자동 빌드  
       5-1) Dockerfile에 기제된 hello_kube.py을 기반으로 Docker기반으로 이미지 생성하고, Github Actions에 자동 푸시
  
   

### 전체 실행 흐름 요약
 main 브랜치에 push 하면 Github Action이 docker-build.yaml을 실행하고, 
