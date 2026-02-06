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