# Capstone_Project-DevOps-Dashboard-for-Resource-and-Monitoring
A DevOps Project for Resource Monitoring of users

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