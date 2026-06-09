# Raw Layer - Bronze
# Stores data exactly as it arrives from sensors - never modified
resource "google_bigquery_dataset" "raw_layer" {
  dataset_id    = "raw_layer"
  friendly_name = "Raw Layer (Bronze)"
  description   = "Raw sensor data - exactly as received, never modified"
  location      = var.location
  project       = var.project_id

  labels = var.labels

  delete_contents_on_destroy = true
}

# Processed Layer - Silver
# Stores cleaned, validated, deduplicated data
resource "google_bigquery_dataset" "processed_layer" {
  dataset_id    = "processed_layer"
  friendly_name = "Processed Layer (Silver)"
  description   = "Cleaned and validated sensor data"
  location      = var.location
  project       = var.project_id

  labels = var.labels

  delete_contents_on_destroy = true
}

# Analytics Layer - Gold
# Stores aggregated, business-ready data
resource "google_bigquery_dataset" "analytics_layer" {
  dataset_id    = "analytics_layer"
  friendly_name = "Analytics Layer (Gold)"
  description   = "Aggregated business-ready data for dashboards and ML"
  location      = var.location
  project       = var.project_id

  labels = var.labels

  delete_contents_on_destroy = true
}

# ML Layer
# Stores BigQuery ML models and predictions
resource "google_bigquery_dataset" "ml_layer" {
  dataset_id    = "ml_layer"
  friendly_name = "ML Layer"
  description   = "BigQuery ML models and prediction results"
  location      = var.location
  project       = var.project_id

  labels = var.labels

  delete_contents_on_destroy = true
}

# Raw Layer Tables
resource "google_bigquery_table" "traffic_raw" {
  dataset_id          = google_bigquery_dataset.raw_layer.dataset_id
  table_id            = "traffic_raw"
  project             = var.project_id
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  clustering = ["sensor_id", "zone_id"]

  labels = var.labels

  schema = jsonencode([
    { name = "sensor_id",       type = "STRING",    mode = "REQUIRED" },
    { name = "zone_id",         type = "STRING",    mode = "REQUIRED" },
    { name = "timestamp",       type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "vehicle_count",   type = "INTEGER",   mode = "NULLABLE" },
    { name = "avg_speed_kmh",   type = "FLOAT",     mode = "NULLABLE" },
    { name = "congestion_level",type = "STRING",    mode = "NULLABLE" },
    { name = "ingested_at",     type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "source",          type = "STRING",    mode = "REQUIRED" }
  ])
}

resource "google_bigquery_table" "air_quality_raw" {
  dataset_id          = google_bigquery_dataset.raw_layer.dataset_id
  table_id            = "air_quality_raw"
  project             = var.project_id
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  clustering = ["sensor_id", "zone_id"]

  labels = var.labels

  schema = jsonencode([
    { name = "sensor_id",     type = "STRING",    mode = "REQUIRED" },
    { name = "zone_id",       type = "STRING",    mode = "REQUIRED" },
    { name = "timestamp",     type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "co2_ppm",       type = "FLOAT",     mode = "NULLABLE" },
    { name = "pm25_ugm3",     type = "FLOAT",     mode = "NULLABLE" },
    { name = "aqi_score",     type = "INTEGER",   mode = "NULLABLE" },
    { name = "temperature_c", type = "FLOAT",     mode = "NULLABLE" },
    { name = "humidity_pct",  type = "FLOAT",     mode = "NULLABLE" },
    { name = "ingested_at",   type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "source",        type = "STRING",    mode = "REQUIRED" }
  ])
}

resource "google_bigquery_table" "energy_raw" {
  dataset_id          = google_bigquery_dataset.raw_layer.dataset_id
  table_id            = "energy_raw"
  project             = var.project_id
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  clustering = ["sensor_id", "zone_id"]

  labels = var.labels

  schema = jsonencode([
    { name = "sensor_id",       type = "STRING",    mode = "REQUIRED" },
    { name = "zone_id",         type = "STRING",    mode = "REQUIRED" },
    { name = "timestamp",       type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "consumption_kwh", type = "FLOAT",     mode = "NULLABLE" },
    { name = "voltage_v",       type = "FLOAT",     mode = "NULLABLE" },
    { name = "power_factor",    type = "FLOAT",     mode = "NULLABLE" },
    { name = "ingested_at",     type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "source",          type = "STRING",    mode = "REQUIRED" }
  ])
}