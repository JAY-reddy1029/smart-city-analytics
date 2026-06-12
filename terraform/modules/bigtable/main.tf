# Bigtable Instance
# We use the DEVELOPMENT tier - it's free and perfect for learning
# In production this would be PRODUCTION tier with multiple nodes
resource "google_bigtable_instance" "main" {
  name    = "smart-city-bigtable"
  project = var.project_id
  labels  = var.labels

  # DEVELOPMENT = single node, free tier
  # Perfect for our learning project
  cluster {
    cluster_id   = "smart-city-cluster"
    zone         = "asia-south1-a"
    num_nodes    = 1
    storage_type = "HDD"
  }

  deletion_protection = false
}

# Table 1: Latest traffic readings
# Stores the most recent reading from every traffic sensor
# Row key design: zone_id#sensor_id
# This allows us to query "all sensors in zone 3" efficiently
resource "google_bigtable_table" "traffic_latest" {
  name          = "traffic_latest"
  project       = var.project_id
  instance_name = google_bigtable_instance.main.name

  # Column families group related columns together
  column_family {
    family = "readings"
  }

  column_family {
    family = "metadata"
  }
}

# Table 2: Latest air quality readings
# Row key design: zone_id#sensor_id
resource "google_bigtable_table" "air_quality_latest" {
  name          = "air_quality_latest"
  project       = var.project_id
  instance_name = google_bigtable_instance.main.name

  column_family {
    family = "readings"
  }

  column_family {
    family = "metadata"
  }
}

# Table 3: Latest energy readings
# Row key design: zone_id#sensor_id
resource "google_bigtable_table" "energy_latest" {
  name          = "energy_latest"
  project       = var.project_id
  instance_name = google_bigtable_instance.main.name

  column_family {
    family = "readings"
  }

  column_family {
    family = "metadata"
  }
}

# Table 4: Sensor alerts
# Stores active alerts when readings cross thresholds
# Row key design: alert_type#zone_id#timestamp
resource "google_bigtable_table" "sensor_alerts" {
  name          = "sensor_alerts"
  project       = var.project_id
  instance_name = google_bigtable_instance.main.name

  column_family {
    family = "alert"
  }
}