# Kestra Orchestration for Stock Market dbt Project

This directory contains the configuration files and workflows for orchestrating the stock market dbt project using Kestra.

## What is Kestra?

Kestra is an open-source orchestration and scheduling platform that helps you automate, schedule, and monitor your data pipelines. It provides a user-friendly interface to manage workflows and track their execution.

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- GCP service account key with BigQuery permissions
- Git repository access

### Setup Steps

1. Navigate to the kestra directory:
   ```
   cd kestra
   ```

2. Make the setup script executable:
   ```
   chmod +x setup_kestra.sh
   ```

3. Run the setup script:
   ```
   ./setup_kestra.sh
   ```

4. Follow the prompts to enter your GCP Project ID and the path to your service account key file.

5. Once the setup is complete, Kestra will be running in Docker containers. You can access the UI at http://localhost:8081.

## Workflow Details

The `stock_market_dbt_workflow.yml` file defines a workflow that:

1. Clones the repository from GitHub
2. Installs necessary dependencies
3. Runs dbt models in sequence (staging → intermediate → marts)
4. Performs data quality checks
5. Sends a notification on successful completion

The workflow is scheduled to run daily at 2 AM, but can also be triggered manually through the Kestra UI.

## Directory Structure

```
kestra/
├── application.yml         # Kestra configuration
├── docker-compose.yml      # Docker Compose configuration
├── flows/                  # Workflow definitions
│   └── stock_market_dbt_workflow.yml
├── plugins/                # Custom plugins (if any)
├── secrets/                # Secret values (gitignored)
├── data/                   # Kestra data storage
├── service-account-key.json # GCP service account key (gitignored)
├── setup_kestra.sh         # Setup script
└── README.md               # This file
```

## Configuration for Multiple Kestra Instances

This Kestra setup is configured to avoid conflicts with other Kestra instances you might have running:

- Uses port 8081 instead of the default 8080
- Uses unique container names with "stock-market" prefix
- Uses a dedicated PostgreSQL database named "kestra_stock"
- Uses a dedicated Docker network named "kestra-stock-network"

If you need to change these settings to avoid conflicts with other instances, edit the following files:

1. `docker-compose.yml`: Update port mappings, container names, and network names
2. `application.yml`: Update database connection details
3. `setup_kestra.sh`: Update the URL in the final echo statement

## Troubleshooting

- If you encounter issues with the Docker containers, you can check the logs with:
  ```
  docker-compose logs -f
  ```

- If the workflow fails, check the execution details in the Kestra UI for error messages.

- To restart Kestra:
  ```
  docker-compose down
  docker-compose up -d
  ```

## Additional Resources

- [Kestra Documentation](https://kestra.io/docs)
- [dbt Documentation](https://docs.getdbt.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
