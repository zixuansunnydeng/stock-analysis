#!/usr/bin/env python3
"""
Script to download the US stock market dataset from Kaggle and load it into GCP.
"""

import os
import subprocess
import argparse
from google.cloud import storage
from google.cloud import bigquery

def setup_kaggle_credentials():
    """Set up Kaggle API credentials."""
    print("Setting up Kaggle credentials...")
    
    # Create .kaggle directory if it doesn't exist
    kaggle_dir = os.path.expanduser('~/.kaggle')
    os.makedirs(kaggle_dir, exist_ok=True)
    
    # Check if kaggle.json already exists
    kaggle_json = os.path.join(kaggle_dir, 'kaggle.json')
    if os.path.exists(kaggle_json):
        print(f"Found existing Kaggle credentials at {kaggle_json}")
        return True
    
    # If not, check if KAGGLE_USERNAME and KAGGLE_KEY are set
    if not os.environ.get('KAGGLE_USERNAME') or not os.environ.get('KAGGLE_KEY'):
        print("Please set KAGGLE_USERNAME and KAGGLE_KEY environment variables")
        print("or create a ~/.kaggle/kaggle.json file manually.")
        print("You can find your API credentials in your Kaggle account settings.")
        return False
    
    # Create kaggle.json file from environment variables
    with open(kaggle_json, 'w') as f:
        f.write('{{"username":"{0}","key":"{1}"}}'.format(
            os.environ.get('KAGGLE_USERNAME'),
            os.environ.get('KAGGLE_KEY')
        ))
    os.chmod(kaggle_json, 0o600)  # Set permissions to be user-readable only
    print(f"Created Kaggle credentials file at {kaggle_json}")
    
    return True

def download_dataset(dataset_name, output_dir):
    """Download dataset from Kaggle."""
    print(f"Downloading dataset {dataset_name} to {output_dir}...")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        subprocess.run([
            'kaggle', 'datasets', 'download', 
            '--path', output_dir, 
            '--unzip', 
            dataset_name
        ], check=True)
        print("Dataset downloaded successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error downloading dataset: {e}")
        return False

def upload_to_gcs(local_dir, bucket_name, prefix=""):
    """Upload files to Google Cloud Storage."""
    print(f"Uploading files from {local_dir} to gs://{bucket_name}/{prefix}...")
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_dir)
            blob_name = os.path.join(prefix, relative_path)
            
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(local_path)
            print(f"Uploaded {local_path} to gs://{bucket_name}/{blob_name}")
    
    return True

def create_bigquery_table(project_id, dataset_id, table_id, gcs_uri, schema=None):
    """Create a BigQuery table from a GCS file."""
    print(f"Creating BigQuery table {project_id}.{dataset_id}.{table_id} from {gcs_uri}...")
    
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    
    # Try an approach with field name transformation
    print("Using approach with field name transformation...")
    
    # Read the CSV file to get the header
    import csv
    with open(os.path.join("./data", os.path.basename(gcs_uri.split('/')[-1])), 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
    
    # Create schema with sanitized field names
    schema = []
    for field_name in header:
        # Replace problematic characters with underscores
        sanitized_name = field_name.replace('.', '_').replace(' ', '_').replace('-', '_')
        schema.append(bigquery.SchemaField(sanitized_name, "STRING"))
    
    # Configure the job with the schema
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.skip_leading_rows = 1
    job_config.schema = schema
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
    
    # Start the load job with the schema
    load_job = client.load_table_from_uri(
        gcs_uri, table_ref, job_config=job_config
    )
    
    try:
        load_job.result()
        table = client.get_table(table_ref)
        print(f"Successfully loaded {table.num_rows} rows with transformed field names.")
        return True
    except Exception as e:
        print(f"Loading failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Download and load Kaggle dataset to GCP')
    parser.add_argument('--project-id', required=True, help='GCP Project ID')
    parser.add_argument('--bucket-name', required=True, help='GCS Bucket Name')
    parser.add_argument('--dataset-id', required=True, help='BigQuery Dataset ID')
    parser.add_argument('--kaggle-dataset', default='saketk511/2019-2024-us-stock-market-data', 
                        help='Kaggle dataset name (default: saketk511/2019-2024-us-stock-market-data)')
    parser.add_argument('--output-dir', default='./data', help='Local directory to store downloaded data')
    
    args = parser.parse_args()
    
    # Set GCP project
    os.environ['GOOGLE_CLOUD_PROJECT'] = args.project_id
    
    # Setup Kaggle credentials
    if not setup_kaggle_credentials():
        return
    
    # Download dataset
    if not download_dataset(args.kaggle_dataset, args.output_dir):
        return
    
    # Upload to GCS
    if not upload_to_gcs(args.output_dir, args.bucket_name, "stock_data"):
        return
    
    # Create BigQuery table(s)
    # Note: This is a simplified example. You might need to adjust based on the actual files in the dataset
    csv_files = [f for f in os.listdir(args.output_dir) if f.endswith('.csv')]
    
    for csv_file in csv_files:
        table_id = os.path.splitext(csv_file)[0].lower().replace(' ', '_')
        gcs_uri = f"gs://{args.bucket_name}/stock_data/{csv_file}"
        
        create_bigquery_table(
            args.project_id,
            args.dataset_id,
            table_id,
            gcs_uri
        )
    
    print("Data pipeline completed successfully!")

if __name__ == "__main__":
    main()
