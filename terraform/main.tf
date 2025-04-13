terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.85.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Create a new GCP Project (if needed)
resource "google_project" "stock_market_project" {
  count           = var.create_new_project ? 1 : 0
  name            = var.project_name
  project_id      = var.project_id
  billing_account = var.billing_account_id
}

# Enable required APIs
resource "google_project_service" "bigquery" {
  project = var.project_id
  service = "bigquery.googleapis.com"
  disable_dependent_services = false
}

resource "google_project_service" "storage" {
  project = var.project_id
  service = "storage.googleapis.com"
  disable_dependent_services = false
}

# Create a Cloud Storage bucket for staging data
resource "google_storage_bucket" "stock_data_bucket" {
  name     = "${var.project_id}-stock-data"
  location = var.region
  force_destroy = true

  uniform_bucket_level_access = true
}

# Create BigQuery dataset
resource "google_bigquery_dataset" "stock_market_dataset" {
  dataset_id                  = var.bigquery_dataset_id
  friendly_name               = "Stock Market Data"
  description                 = "Dataset containing US stock market data from 2019-2024"
  location                    = var.region
  delete_contents_on_destroy  = true
}

# Create service account for dbt
resource "google_service_account" "dbt_service_account" {
  account_id   = "dbt-service-account"
  display_name = "DBT Service Account"
  description  = "Service account for dbt to access BigQuery"
}

# Grant BigQuery Admin role to the service account
resource "google_project_iam_member" "dbt_bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.dbt_service_account.email}"
}

# Grant Storage Object Admin role to the service account
resource "google_project_iam_member" "dbt_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.dbt_service_account.email}"
}

# Create service account key (optional - for local development)
resource "google_service_account_key" "dbt_sa_key" {
  service_account_id = google_service_account.dbt_service_account.name
}

# Output the service account key to a local file
resource "local_file" "dbt_sa_key_file" {
  content  = base64decode(google_service_account_key.dbt_sa_key.private_key)
  filename = "${path.module}/../dbt_service_account_key.json"
}
