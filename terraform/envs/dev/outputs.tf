output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "vpc_name" {
  description = "VPC network name"
  value       = module.networking.vpc_name
}

output "raw_data_bucket" {
  description = "Raw data GCS bucket name"
  value       = module.cloudrun.raw_data_bucket_name
}

output "dataflow_staging_bucket" {
  description = "Dataflow staging bucket name"
  value       = module.cloudrun.dataflow_staging_bucket_name
}

output "artifact_registry_url" {
  description = "Docker registry URL"
  value       = module.cloudrun.artifact_registry_url
}

output "bigtable_instance" {
  description = "Bigtable instance name"
  value       = module.bigtable.instance_name
}

output "bigquery_datasets" {
  description = "BigQuery dataset IDs"
  value = {
    raw       = module.bigquery.raw_layer_id
    processed = module.bigquery.processed_layer_id
    analytics = module.bigquery.analytics_layer_id
    ml        = module.bigquery.ml_layer_id
  }
}

output "pubsub_topics" {
  description = "Pub/Sub topic IDs"
  value = {
    traffic       = module.pubsub.traffic_topic_name
    air_quality   = module.pubsub.air_quality_topic_name
    energy        = module.pubsub.energy_topic_name
    citizen       = module.pubsub.citizen_events_topic_id
    dead_letter   = module.pubsub.dead_letter_topic_id
  }
}

output "data_pipeline_sa" {
  description = "Data pipeline service account email"
  value       = google_service_account.data_pipeline.email
}

output "api_sa" {
  description = "API service account email"
  value       = google_service_account.api.email
}