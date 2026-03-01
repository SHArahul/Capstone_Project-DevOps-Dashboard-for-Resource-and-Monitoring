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

## For Demo point of view, minikube on EC2 is opt but EKS cluster orchestration is favoured for prod like deployment.



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
<img width="1883" height="299" alt="curl-service-python-api" src="https://github.com/user-attachments/assets/66e8129c-1f4f-4433-9db5-ab42e7f9d2ef" />  
<img width="1512" height="460" alt="pod-exec-postgres" src="https://github.com/user-attachments/assets/889d469b-2a95-4e09-8cc0-da239c76a4b3" />  
<img width="1907" height="886" alt="pods-deploy-secret-svc-config" src="https://github.com/user-attachments/assets/42b64229-a18d-4389-a9ad-89186734b658" />  

###Grafana-Dashboard
<img width="1908" height="894" alt="Screenshot 2026-02-28 005151" src="https://github.com/user-attachments/assets/44041f59-24ac-4c41-9f3a-046d078bb1ab" />

<img width="1914" height="695" alt="Screenshot 2026-03-01 111732" src="https://github.com/user-attachments/assets/b7bd7308-b286-429b-b0be-20b359b26c06" />

<img width="1917" height="618" alt="Screenshot 2026-03-01 111806" src="https://github.com/user-attachments/assets/0910f332-69a5-4765-bdf2-f3c47c34fec2" />



# Conclusion

This Cloud Cost Monitoring Dashboard provides a scalable, automated, and cloud-native solution for multi-cloud cost observability.

By combining:

Incremental cost ingestion via Flask API

Structured time-series storage in PostgreSQL

Containerized deployment on EKS

Grafana-based visualization

The platform transforms raw billing data into operational cost intelligence.

## Created by:

Rahul Sharma | Harshwerdhan Roy | Vignesh Raja

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

# Kubernetes Port Forwarding – Complete Guide

## Overview

This document explains how to use `kubectl port-forward` to access a Kubernetes Service from your local machine or other systems in the same network.

Port forwarding creates a temporary tunnel between your local machine and a Pod or Service inside the Kubernetes cluster. It is mainly used for debugging, testing, and internal access.

---

## 🛠 Prerequisites

Make sure the following are available:

- A running Kubernetes cluster (Minikube / Kind / EKS / AKS / etc.)
- kubectl installed and configured
- A deployed Service named `my-service`

Verify cluster connection:

```bash
kubectl get nodes
```

Verify service:

```bash
kubectl get svc
```

---

## Port Forward Command

```bash
kubectl port-forward --address 0.0.0.0 service/my-service 8080:80
```

---

## Command Explanation

| Part | Meaning |
|------|---------|
| kubectl port-forward | Creates a temporary tunnel |
| --address 0.0.0.0 | Listens on all network interfaces |
| service/my-service | Target Kubernetes Service |
| 8080:80 | Maps local port 8080 to service port 80 |

This means:

- Listen on `0.0.0.0:8080` (accessible from other machines)
- Forward traffic to port `80` of `my-service` inside the cluster

---

##  Network Flow

Browser  
   ↓  
Local Machine (0.0.0.0:8080)  
   ↓  
kubectl Tunnel  
   ↓  
Kubernetes Service (my-service:80)  
   ↓  
Pod  

---

##  Accessing the Application

### From Local Machine

```
http://localhost:8080
```

### From Another Machine in Same Network

Find your local IP:

```bash
ip a
```

Then access:

```
http://<your-local-ip>:8080
```

Example:

```
http://192.168.1.20:8080
```

---

##  Port Forward a Pod (Optional)

Instead of forwarding a Service, you can forward directly to a Pod:

```bash
kubectl port-forward pod/<pod-name> 8080:80
```

---

## Security Considerations

- Using `--address 0.0.0.0` exposes the port to your entire network.
- Do NOT use this method in production.
- For cloud VMs (e.g., AWS EC2), ensure the Security Group allows port 8080.
- This is a temporary tunnel, not a permanent exposure.

---

##  Port Forward vs NodePort vs LoadBalancer

| Feature | Port Forward | NodePort | LoadBalancer |
|----------|-------------|----------|--------------|
| Temporary | Yes | No | No |
| Production Ready | No | Limited | Yes |
| Requires Cloud Provider | No | No | Yes |
| Easy Debugging | Yes | No | No |

---



## Best Use Cases

- Debugging applications
- Testing services locally
- Temporary demo environments
- Accessing internal cluster services


