# Cloud Storage bucket for raw data landing zone
# CSV files, batch uploads land here first
resource "google_storage_bucket" "raw_data" {
  name          = "${var.project_id}-raw-data"
  project       = var.project_id
  location      = var.region
  force_destroy = true

  labels = var.labels

  # Automatically delete files after 90 days
  # Raw files are archived to BigQuery so we don't need them forever
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  # Move files to cheaper storage after 30 days
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  versioning {
    enabled = true
  }

  uniform_bucket_level_access = true
}

# Cloud Storage bucket for Dataflow staging
# Dataflow needs a bucket to store temporary files while running
resource "google_storage_bucket" "dataflow_staging" {
  name          = "${var.project_id}-dataflow-staging"
  project       = var.project_id
  location      = var.region
  force_destroy = true

  labels = var.labels

  lifecycle_rule {
    condition {
      age = 7
    }
    action {
      type = "Delete"
    }
  }

  uniform_bucket_level_access = true
}

# Cloud Storage bucket for Cloud Build artifacts
# Cloud Build stores build outputs here
resource "google_storage_bucket" "build_artifacts" {
  name          = "${var.project_id}-build-artifacts"
  project       = var.project_id
  location      = var.region
  force_destroy = true

  labels = var.labels

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  uniform_bucket_level_access = true
}

# Cloud Storage bucket for ML artifacts
# Vertex AI stores model files, training data here
resource "google_storage_bucket" "ml_artifacts" {
  name          = "${var.project_id}-ml-artifacts"
  project       = var.project_id
  location      = var.region
  force_destroy = true

  labels = var.labels

  versioning {
    enabled = true
  }

  uniform_bucket_level_access = true
}

# Artifact Registry repository for Docker images
# All our Cloud Run containers are stored here
resource "google_artifact_registry_repository" "main" {
  repository_id = "smart-city-repo"
  project       = var.project_id
  location      = var.region
  format        = "DOCKER"
  description   = "Docker images for Smart City Analytics Platform"

  labels = var.labels
}