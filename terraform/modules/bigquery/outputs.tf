output "raw_layer_id" {
  description = "Raw layer dataset ID"
  value       = google_bigquery_dataset.raw_layer.dataset_id
}

output "processed_layer_id" {
  description = "Processed layer dataset ID"
  value       = google_bigquery_dataset.processed_layer.dataset_id
}

output "analytics_layer_id" {
  description = "Analytics layer dataset ID"
  value       = google_bigquery_dataset.analytics_layer.dataset_id
}

output "ml_layer_id" {
  description = "ML layer dataset ID"
  value       = google_bigquery_dataset.ml_layer.dataset_id
}