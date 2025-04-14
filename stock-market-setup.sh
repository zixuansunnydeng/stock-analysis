#!/bin/bash
# Setup script for Kestra orchestration with Docker

# Create required directories
mkdir -p flows
mkdir -p plugins
mkdir -p secrets
mkdir -p data

# Set up secrets
echo "Setting up secrets..."

# Use default values for testing
GCP_PROJECT_ID="your-gcp-project-id"
DBT_SERVICE_ACCOUNT_KEY_PATH="dbt_service_account_key.json"

# Save secrets
echo "$GCP_PROJECT_ID" > secrets/GCP_PROJECT_ID
cp "$DBT_SERVICE_ACCOUNT_KEY_PATH" service-account-key.json
echo "{}" > secrets/DBT_SERVICE_ACCOUNT_KEY  # Empty JSON object as placeholder

echo "Secrets configured successfully!"

# Start Kestra with Docker Compose
echo "Starting Kestra with Docker Compose..."
docker-compose -f stock-market-docker-compose.yml up -d

echo "Kestra is starting up. You can access the UI at http://localhost:8080"
echo "It may take a few moments for the services to fully initialize."
echo "Note: This Kestra instance is configured to avoid conflicts with other Kestra instances."
