output "project_id" {
  value       = var.project_id
  description = "The GCP project ID"
}

output "bigquery_dataset_id" {
  value       = google_bigquery_dataset.stock_market_dataset.dataset_id
  description = "The BigQuery dataset ID"
}

output "storage_bucket_name" {
  value       = google_storage_bucket.stock_data_bucket.name
  description = "The GCS bucket name for stock data"
}

output "dbt_service_account_email" {
  value       = google_service_account.dbt_service_account.email
  description = "The email of the service account for dbt"
}

output "service_account_key_location" {
  value       = local_file.dbt_sa_key_file.filename
  description = "Location of the service account key file"
  sensitive   = true
}
