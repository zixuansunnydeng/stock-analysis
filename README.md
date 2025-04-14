# Stock Market dbt Project

This project demonstrates how to use dbt (data build tool) with GCP BigQuery to analyze US stock market data from 2019-2024. The project uses Terraform to set up the GCP infrastructure, downloads data from Kaggle, and transforms it using dbt models.

## Project Structure

```
.
├── dbt_project/            # dbt project files
│   ├── models/             # dbt models
│   │   ├── staging/        # Staging models for data cleaning
│   │   ├── intermediate/   # Intermediate models for metrics calculation
│   │   └── marts/          # Mart models for aggregated analytics
│   ├── dbt_project.yml     # dbt project configuration
│   └── profiles.yml.example # Example dbt profile configuration
├── terraform/              # Terraform configuration
│   ├── main.tf             # Main Terraform configuration
│   ├── variables.tf        # Terraform variables
│   ├── outputs.tf          # Terraform outputs
│   └── terraform.tfvars    # Terraform variables with your GCP project details
├── kestra/                 # Kestra orchestration
│   ├── docker-compose.yml  # Docker Compose configuration
│   ├── application.yml     # Kestra configuration
│   ├── stock_market_dbt_workflow.yml # Workflow definition
│   ├── setup_kestra.sh     # Setup script for Kestra
│   └── README.md           # Kestra documentation
├── scripts/                # Utility scripts
│   ├── download_and_load_data_fixed.py # Script to download and load data
│   ├── transform_csv_fixed.py # Script to transform CSV for BigQuery compatibility
│   └── setup.sh            # Setup script to streamline installation
├── stock_market_analysis.ipynb # Jupyter notebook for data visualization
├── data/                   # Local data directory (gitignored)
├── dbt_service_account_key.json # Service account key for dbt (gitignored)
└── README.md               # This file
```

## Prerequisites

- GCP account with billing enabled
- Terraform installed
- dbt installed
- Python 3.7+ installed
- Kaggle account and API credentials
- Docker and Docker Compose (for Kestra orchestration)

## Setup Instructions

### 1. Set up GCP with Terraform

1. Create or edit `terraform/terraform.tfvars` with your GCP project details:
   ```
   project_id         = "your-gcp-project-id"  # Replace with your actual GCP project ID
   project_name       = "Stock Market DBT Project"
   create_new_project = false
   # billing_account_id = "your-billing-account-id"  # Uncomment if creating a new project
   region             = "us-central1"
   bigquery_dataset_id = "stock_market_data"
   ```

2. Authenticate with GCP:
   ```
   gcloud auth application-default login
   ```

3. Initialize and apply Terraform:
   ```
   cd terraform
   terraform init -upgrade
   terraform apply
   ```

   This will create:
   - A BigQuery dataset
   - A Cloud Storage bucket
   - A service account for dbt
   - Required API enablements

### 2. Download and Load Data

1. Set up Kaggle API credentials:

   Create a file at `~/.kaggle/kaggle.json` with your Kaggle credentials:
   ```json
   {
     "username": "your-kaggle-username",
     "key": "your-kaggle-api-key"
   }
   ```

   Make sure the file has the correct permissions:
   ```
   chmod 600 ~/.kaggle/kaggle.json
   ```

2. Install required Python packages:
   ```
   pip install kaggle google-cloud-storage google-cloud-bigquery
   ```

3. Run the data download and transformation scripts:
   ```
   # Download and upload data to GCS
   python scripts/download_and_load_data_fixed.py \
     --project-id=your-gcp-project-id \
     --bucket-name=your-gcp-project-id-stock-data \
     --dataset-id=stock_market_data

   # If needed, transform the CSV for BigQuery compatibility
   python scripts/transform_csv_fixed.py \
     --input-file="data/Stock Market Dataset.csv" \
     --output-file="data/stock_market_transformed_fixed.csv"

   # Upload the transformed CSV to GCS
   gsutil cp data/stock_market_transformed_fixed.csv gs://your-gcp-project-id-stock-data/stock_data/

   # Create BigQuery table from the transformed CSV
   bq load --autodetect --source_format=CSV \
     stock_market_data.stock_market_raw \
     gs://your-gcp-project-id-stock-data/stock_data/stock_market_transformed_fixed.csv
   ```

   This process:
   - Downloads the stock market dataset from Kaggle
   - Transforms the CSV to make it compatible with BigQuery
   - Uploads the data to your GCS bucket
   - Creates BigQuery tables from the data

### 3. Set up dbt

1. Create the dbt profiles file:
   ```
   mkdir -p ~/.dbt
   ```

   Create a file at `~/.dbt/profiles.yml` with the following content:
   ```yaml
   stock_market:
     target: dev
     outputs:
       dev:
         type: bigquery
         method: service-account
         project: your-gcp-project-id  # Replace with your actual GCP project ID
         dataset: stock_market_data
         threads: 4
         keyfile: /full/path/to/dbt_service_account_key.json  # Use absolute path
         timeout_seconds: 300
         location: us-central1  # Must match your dataset location
         priority: interactive
   ```

2. Create the required BigQuery datasets with the correct location:
   ```
   # Create datasets for dbt models
   bq mk --dataset --location=us-central1 your-gcp-project-id:stock_market_data_staging
   bq mk --dataset --location=us-central1 your-gcp-project-id:stock_market_data_intermediate
   bq mk --dataset --location=us-central1 your-gcp-project-id:stock_market_data_marts
   ```

3. Test the dbt connection:
   ```
   cd dbt_project
   dbt debug
   ```

4. Run dbt models:
   ```
   dbt run
   ```

   This will create the following models in BigQuery:
   - Staging models: Raw data cleaning and standardization
   - Intermediate models: Daily stock metrics calculations
   - Mart models: Aggregated stock performance metrics

### 4. Set up Kestra Orchestration (Optional)

Kestra is used to orchestrate the dbt workflow, providing scheduling, monitoring, and error handling.

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

5. Once the setup is complete, Kestra will be running in Docker containers. You can access the UI at http://localhost:8082.

6. The workflow is configured to run daily at 2 AM, but you can also trigger it manually through the Kestra UI.

For more details on the Kestra setup, see the [kestra/README.md](kestra/README.md) file.

## Data Models

### Staging Models
- `stg_stock_prices`: Cleans and standardizes raw stock market data
  - Converts date strings to proper date format
  - Renames columns to more descriptive names
  - Organizes fields by asset type (stocks, commodities, cryptocurrencies)
  - Adds metadata fields

### Intermediate Models
- `int_daily_stock_metrics`: Preserves detailed data and adds calculated metrics
  - Maintains all price and volume data for various assets
  - Calculates average prices by asset class (tech stocks, commodities, cryptocurrencies)
  - Prepares data for aggregation

### Mart Models
- `stock_performance`: Aggregates stock performance metrics by month
  - Monthly average prices for major indices (S&P 500, Nasdaq)
  - Monthly average prices for tech stocks (Apple, Microsoft, Google, etc.)
  - Monthly average prices for commodities (Gold, Oil, etc.)
  - Monthly average prices for cryptocurrencies (Bitcoin, Ethereum)
  - Aggregated metrics by asset class

## Troubleshooting

### Common Issues

1. **Terraform Provider Errors**
   - If you encounter provider version conflicts, run `terraform init -upgrade`
   - Make sure you have authenticated with GCP using `gcloud auth application-default login`

2. **Kaggle API Issues**
   - Ensure your kaggle.json file is in the correct location (~/.kaggle/kaggle.json)
   - Check that the file has the correct permissions (chmod 600)

3. **dbt Connection Issues**
   - Verify that the service account key file exists and is referenced correctly in profiles.yml
   - Make sure the BigQuery dataset exists with the correct location (us-central1)
   - Check that the service account has the necessary permissions
   - Grant the service account the BigQuery Data Owner role:
     ```
     gcloud projects add-iam-policy-binding your-gcp-project-id \
       --member="serviceAccount:dbt-service-account@your-gcp-project-id.iam.gserviceaccount.com" \
       --role="roles/bigquery.dataOwner"
     ```

4. **CSV Format Issues**
   - If you encounter issues with the CSV format when loading to BigQuery, use the transformation script
   - BigQuery has specific requirements for column names (no periods, special characters)
   - The transformation script handles these requirements

## Results and Visualization

After running the dbt models, you can query the data in BigQuery to analyze stock market trends:

```sql
-- Example query to see monthly performance by asset class
SELECT
  month,
  avg_sp500_price,
  avg_tech_price,
  avg_commodity_price,
  avg_crypto_price
FROM
  `your-gcp-project-id.stock_market_data_marts.stock_performance`
ORDER BY
  month DESC
LIMIT 10;
```

You can visualize this data using:
- Google Data Studio (Looker Studio)
- Tableau
- Power BI
- Python libraries like Matplotlib or Plotly

## Next Steps

Possible enhancements to this project:

1. **Add more advanced analytics models**:
   - Correlation analysis between different assets
   - Volatility calculations
   - Moving averages and technical indicators

2. **Enhance the orchestration**:
   - Customize the Kestra workflow for your specific needs
   - Add more data quality checks
   - Configure email notifications for workflow failures
   - Set up a CI/CD pipeline for the workflow

3. **Create a dashboard**:
   - Build a Looker Studio dashboard for visualizing the data
   - Add interactive filters and time series charts

## Contributing

Feel free to submit issues or pull requests to improve this project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
