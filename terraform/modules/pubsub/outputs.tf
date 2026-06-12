output "traffic_topic_id" {
  description = "Traffic data Pub/Sub topic ID"
  value       = google_pubsub_topic.traffic_data.id
}

output "traffic_topic_name" {
  description = "Traffic data Pub/Sub topic name"
  value       = google_pubsub_topic.traffic_data.name
}

output "air_quality_topic_id" {
  description = "Air quality data Pub/Sub topic ID"
  value       = google_pubsub_topic.air_quality_data.id
}

output "air_quality_topic_name" {
  description = "Air quality data Pub/Sub topic name"
  value       = google_pubsub_topic.air_quality_data.name
}

output "energy_topic_id" {
  description = "Energy data Pub/Sub topic ID"
  value       = google_pubsub_topic.energy_data.id
}

output "energy_topic_name" {
  description = "Energy data Pub/Sub topic name"
  value       = google_pubsub_topic.energy_data.name
}

output "citizen_events_topic_id" {
  description = "Citizen events Pub/Sub topic ID"
  value       = google_pubsub_topic.citizen_events.id
}

output "dead_letter_topic_id" {
  description = "Dead letter Pub/Sub topic ID"
  value       = google_pubsub_topic.dead_letter.id
}