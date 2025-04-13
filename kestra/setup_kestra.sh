#!/bin/bash
# Setup script for Kestra orchestration with Docker

# Create required directories
mkdir -p flows
mkdir -p plugins
mkdir -p secrets
mkdir -p data

# Copy workflow file to flows directory
cp stock_market_dbt_workflow.yml flows/

# Set up secrets
echo "Setting up secrets..."
echo "Please enter your GCP Project ID:"
read GCP_PROJECT_ID

echo "Please provide the path to your dbt service account key file:"
read DBT_SERVICE_ACCOUNT_KEY_PATH

# Save secrets
echo "$GCP_PROJECT_ID" > secrets/GCP_PROJECT_ID
cp "$DBT_SERVICE_ACCOUNT_KEY_PATH" service-account-key.json
cat "$DBT_SERVICE_ACCOUNT_KEY_PATH" > secrets/DBT_SERVICE_ACCOUNT_KEY

echo "Secrets configured successfully!"

# Start Kestra with Docker Compose
echo "Starting Kestra with Docker Compose..."
docker-compose up -d

echo "Kestra is starting up. You can access the UI at http://localhost:8081"
echo "It may take a few moments for the services to fully initialize."
echo "Note: This Kestra instance is configured to avoid conflicts with other Kestra instances."
