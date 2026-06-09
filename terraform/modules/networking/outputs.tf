output "vpc_id" {
  description = "VPC network ID"
  value       = google_compute_network.main.id
}

output "vpc_name" {
  description = "VPC network name"
  value       = google_compute_network.main.name
}

output "data_processing_subnet_id" {
  description = "Data processing subnet ID"
  value       = google_compute_subnetwork.data_processing.id
}

output "data_processing_subnet_name" {
  description = "Data processing subnet name"
  value       = google_compute_subnetwork.data_processing.name
}

output "serving_subnet_id" {
  description = "Serving subnet ID"
  value       = google_compute_subnetwork.serving.id
}

output "serving_subnet_name" {
  description = "Serving subnet name"
  value       = google_compute_subnetwork.serving.name
}