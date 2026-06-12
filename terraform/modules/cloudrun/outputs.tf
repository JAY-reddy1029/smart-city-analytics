output "raw_data_bucket_name" {
  description = "Raw data GCS bucket name"
  value       = google_storage_bucket.raw_data.name
}

output "raw_data_bucket_url" {
  description = "Raw data GCS bucket URL"
  value       = google_storage_bucket.raw_data.url
}

output "dataflow_staging_bucket_name" {
  description = "Dataflow staging GCS bucket name"
  value       = google_storage_bucket.dataflow_staging.name
}

output "dataflow_staging_bucket_url" {
  description = "Dataflow staging GCS bucket URL"
  value       = google_storage_bucket.dataflow_staging.url
}

output "ml_artifacts_bucket_name" {
  description = "ML artifacts GCS bucket name"
  value       = google_storage_bucket.ml_artifacts.name
}

output "artifact_registry_url" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/smart-city-repo"
}