# Capstone_Project-DevOps-Dashboard-for-Resource-and-Monitoring
A DevOps Project for Resource Monitoring of users

# Architecture Diagram
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/f261d2f7-e4d1-4f23-9a6c-094ff92fd5b2" />

# Repository Structure

```
├── api/
│   ├── all_endpoint.py                    # Flask API entrypoint
|   ├── Dockerfile
├── fetcher/
│   ├── fetch_aws_cost.py
│   ├── azure_cost_fetch.py
│   └── db_utils.py
├── requirements.txt
│
├── database/
│   ├── aws_dashboard.sql              # grafana dashboard query
│   ├── azure_dashboard.sql
│
│
├── k8s/
│   ├── pythonapi-deployment.yaml
│   ├── pythonapi-service.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── grafana-deployment.yaml
│   ├── grafana-service.yaml
│
├── terraform/
│   ├── vpc/
│   ├── eks/
|   ├── iam/
│
└── README.md
```
## Problem Statement

Organizations operating across Amazon Web Services and Microsoft Azure lack a unified, engineering-level cost observability layer.

Native cloud billing tools:

Are provider-specific and siloed

Focus on billing summaries rather than operational analytics

Offer limited long-term structured storage for custom queries

Do not integrate seamlessly into DevOps workflows

As a result:

Engineers cannot easily correlate cost with service, region, or usage trends.

Finance sees aggregated numbers without technical attribution.

Cost spikes are detected late.

Historical trend analysis requires manual exports.

## What This Dashboard Enables

Daily incremental cost ingestion

Time-series cost storage in PostgreSQL

Service-wise and region-wise breakdown

Cross-cloud cost comparison (AWS vs Azure)

SQL-driven cost intelligence

Grafana-based operational dashboards

# EKS Deployment Guide

This section explains how to deploy the complete Cloud Cost Monitoring stack on Amazon Web Services using Amazon EKS.

## Prerequisites

Install locally:

AWS CLI

kubectl

eksctl or Terraform

Docker

Helm (optional

## Provision EKS Cluster

```
eksctl create cluster \
  --name cost-monitoring-cluster \
  --region ca-central-1 \
  --nodes 2 \
  --node-type t3.medium
```

Update kubeconfig:

```
aws eks update-kubeconfig \
  --region ca-central-1 \
  --name cost-monitoring-cluster
```
## Using Terraform

```
cd terraform/vpc
terraform init
terraform apply

cd ../eks
terraform init
terraform apply
```
## Deploy PostgreSQL (Stateful)

Apply manifests:

```
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/postgres-service.yaml
```

Verify:

```
kubectl get pods
kubectl get pvc
```

Ensure:

PVC is Bound

Pod is Running


## Build and Push API Image

```
docker build -t <your-ecr-repo>/python-api:latest -f api/Dockerfile .
```

push to ECR

```
aws ecr get-login-password --region ca-central-1 \
| docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

docker push <your-ecr-repo>/cloud-cost-api:latest
```

## Deploy Flask API
```
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
```

## Deploy Grafana
```
kubectl apply -f k8s/grafana-deployment.yaml
kubectl apply -f k8s/grafana-service.yaml
```

## Configure secrets

```
kubectl create secret generic db-secret \
  --from-literal=DB_USER=admin \
  --from-literal=DB_PASSWORD=password
```
Inject via environment variables in deployment YAML.

For AWS authentication, use:

IAM Roles for Service Accounts (IRSA)

Or AWS Secrets Manager

### Create `.env` file
```
AWS_ACCESS_KEY_ID=''
AWS_SECRET_ACCESS_KEY=''
AWS_REGION=''
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=
DB_NAME=aws_costs_db


# Azure Credentials
AZURE_TENANT_ID=""
AZURE_CLIENT_ID=""
AZURE_CLIENT_SECRET=""
AZURE_SUBSCRIPTION_ID=""

# Azure Database 
AZURE_DB_NAME="azure_costs_db"

# GCP Credentials

# GCP Database
GCP_DB_NAME="gcp_costs_db"
```

All endpoint for fetch details
- /aws-cost
- /azure-cost

For Run (on root dir)
```
python -m api.all_endpoint
```

# Testing & Validation

Infrastructure Validation

```
kubectl get nodes
kubectl get pods -A
kubectl get pvc
```

## API Endpoint Test

Get API LoadBalancer IP:

kubectl get svc

curl http://<external-ip>/aws-cost

# Screenshot


# Conclusion

This Cloud Cost Monitoring Dashboard provides a scalable, automated, and cloud-native solution for multi-cloud cost observability.

By combining:

Incremental cost ingestion via Flask API

Structured time-series storage in PostgreSQL

Containerized deployment on EKS

Grafana-based visualization

The platform transforms raw billing data into operational cost intelligence.

-----------------------

-----------------------

## Minikube Installation
- Prequrities
  - Docker
  - Machine must have above 1800M free memory

- Docker  Installation  
```
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc | cut -f1)
```
```
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
```
```
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
```
sudo usermod -aG docker $USER && newgrp docker
sudo systemctl status docker
```
- Minikube Installation

```
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
```
```
minikube start
```
If driver not detected automatically
```
minikube start --driver=docker
```
```
alias kubectl="minikube kubectl --"
kubectl get po -A
```
