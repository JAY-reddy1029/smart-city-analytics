output "instance_name" {
  description = "Bigtable instance name"
  value       = google_bigtable_instance.main.name
}

output "instance_id" {
  description = "Bigtable instance ID"
  value       = google_bigtable_instance.main.id
}

output "traffic_latest_table" {
  description = "Traffic latest readings table name"
  value       = google_bigtable_table.traffic_latest.name
}

output "air_quality_latest_table" {
  description = "Air quality latest readings table name"
  value       = google_bigtable_table.air_quality_latest.name
}

output "energy_latest_table" {
  description = "Energy latest readings table name"
  value       = google_bigtable_table.energy_latest.name
}

output "sensor_alerts_table" {
  description = "Sensor alerts table name"
  value       = google_bigtable_table.sensor_alerts.name
}