terraform {
  required_version = ">= 1.8.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Common labels applied to every resource
# Makes it easy to find all resources belonging to this project
locals {
  common_labels = {
    project     = "smart-city-analytics"
    environment = var.environment
    managed_by  = "terraform"
    team        = "data-engineering"
  }
}

# Module 1: Networking
# Creates VPC, subnets, firewall rules, Cloud NAT
module "networking" {
  source     = "../../modules/networking"
  project_id = var.project_id
  region     = var.region
  labels     = local.common_labels
}

# Module 2: BigQuery
# Creates all datasets and tables
module "bigquery" {
  source     = "../../modules/bigquery"
  project_id = var.project_id
  location   = var.region
  labels     = local.common_labels
}

# Module 3: Pub/Sub
# Creates all topics and subscriptions
module "pubsub" {
  source     = "../../modules/pubsub"
  project_id = var.project_id
  labels     = local.common_labels
}

# Module 4: Cloud Storage + Artifact Registry
# Creates all GCS buckets and Docker registry
module "cloudrun" {
  source     = "../../modules/cloudrun"
  project_id = var.project_id
  region     = var.region
  labels     = local.common_labels
}

# Module 5: Bigtable
# Creates Bigtable instance and tables
module "bigtable" {
  source     = "../../modules/bigtable"
  project_id = var.project_id
  labels     = local.common_labels
}

# Service Account for Data Pipeline
# This is the identity used by Dataflow, Cloud Run Jobs
# We follow least privilege - only the permissions it needs
resource "google_service_account" "data_pipeline" {
  account_id   = "data-pipeline-sa"
  display_name = "Data Pipeline Service Account"
  description  = "Used by Dataflow and Cloud Run Jobs"
  project      = var.project_id
}

# Service Account for API
# Used by the Cloud Run API service
resource "google_service_account" "api" {
  account_id   = "api-sa"
  display_name = "API Service Account"
  description  = "Used by Cloud Run API"
  project      = var.project_id
}

# IAM: Data pipeline SA permissions
resource "google_project_iam_member" "pipeline_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.data_pipeline.email}"
}

resource "google_project_iam_member" "pipeline_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.data_pipeline.email}"
}

resource "google_project_iam_member" "pipeline_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.data_pipeline.email}"
}

resource "google_project_iam_member" "pipeline_dataflow" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.data_pipeline.email}"
}

resource "google_project_iam_member" "pipeline_bigtable" {
  project = var.project_id
  role    = "roles/bigtable.user"
  member  = "serviceAccount:${google_service_account.data_pipeline.email}"
}

resource "google_project_iam_member" "pipeline_secretmanager" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.data_pipeline.email}"
}

# IAM: API SA permissions
resource "google_project_iam_member" "api_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.api.email}"
}

resource "google_project_iam_member" "api_bigtable" {
  project = var.project_id
  role    = "roles/bigtable.reader"
  member  = "serviceAccount:${google_service_account.api.email}"
}

resource "google_project_iam_member" "api_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.api.email}"
}

resource "google_project_iam_member" "api_secretmanager" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.api.email}"
}