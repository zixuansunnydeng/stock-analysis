variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "project_name" {
  description = "The GCP project name"
  type        = string
  default     = "Stock Market DBT Project"
}

variable "create_new_project" {
  description = "Whether to create a new GCP project"
  type        = bool
  default     = false
}

variable "billing_account_id" {
  description = "The GCP billing account ID (required if creating a new project)"
  type        = string
  default     = ""
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "bigquery_dataset_id" {
  description = "The BigQuery dataset ID"
  type        = string
  default     = "stock_market_data"
}
