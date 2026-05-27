# FastAPI CRUD + EKS + ArgoCD

最小化的 EKS 練習專案，使用 ArgoCD 部署 FastAPI CRUD 應用。

## 專案結構

```
├── app/              FastAPI 應用 + Dockerfile
├── terraform/        EKS 基礎設施 (workspace: dev/prod)
├── k8s/              Kubernetes manifests (ArgoCD sync target)
├── argocd/           ArgoCD Application 定義
└── docker-compose.yaml
```

## 本地開發

```bash
# 啟動
docker compose up --build

# 測試 API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/items/ -H "Content-Type: application/json" -d '{"name":"test","price":9.99}'
curl http://localhost:8000/items/1
curl -X PUT http://localhost:8000/items/1 -H "Content-Type: application/json" -d '{"name":"updated"}'
curl -X DELETE http://localhost:8000/items/1
```

## 部署到 EKS

### 1. Terraform 建立 EKS

```bash
cd terraform
terraform init
terraform workspace new dev
terraform workspace select dev
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```

### 2. 設定 kubeconfig

```bash
aws eks update-kubeconfig --name fastapi-eks-dev --region us-east-1
```

### 3. 安裝 ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 取得初始密碼
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# 開啟 UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

### 4. 建置並推送 Docker Image

```bash
# 建立 ECR repo
aws ecr create-repository --repository-name fastapi-argocd --region us-east-1

# Login ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Build & Push
docker build -t fastapi-argocd ./app
docker tag fastapi-argocd:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fastapi-argocd:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/fastapi-argocd:latest
```

### 5. 更新 k8s/deployment.yaml 中的 image 並推送

替換 `REPLACE_WITH_ECR_IMAGE` 為你的 ECR image URI。

### 6. 部署 ArgoCD Application

```bash
# 更新 argocd/application.yaml 中的 repoURL
kubectl apply -f argocd/application.yaml
```

ArgoCD 會自動同步 `k8s/` 中的 manifests 到 EKS cluster。

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /items/ | Create item |
| GET | /items/{id} | Get item |
| PUT | /items/{id} | Update item |
| DELETE | /items/{id} | Delete item |
