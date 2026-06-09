# Topic 1: Traffic sensor data
resource "google_pubsub_topic" "traffic_data" {
  name    = "traffic-data-topic"
  project = var.project_id
  labels  = var.labels

  message_retention_duration = "86600s"
}

resource "google_pubsub_subscription" "traffic_data_sub" {
  name    = "traffic-data-subscription"
  topic   = google_pubsub_topic.traffic_data.name
  project = var.project_id
  labels  = var.labels

  # How long Pub/Sub keeps undelivered messages (7 days)
  message_retention_duration = "604800s"

  # How long subscriber has to acknowledge a message (60 seconds)
  ack_deadline_seconds = 60

  # Dead letter policy - after 5 failed attempts, send to dead letter topic
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 5
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}

# Topic 2: Air quality sensor data
resource "google_pubsub_topic" "air_quality_data" {
  name    = "air-quality-data-topic"
  project = var.project_id
  labels  = var.labels

  message_retention_duration = "86600s"
}

resource "google_pubsub_subscription" "air_quality_data_sub" {
  name    = "air-quality-data-subscription"
  topic   = google_pubsub_topic.air_quality_data.name
  project = var.project_id
  labels  = var.labels

  message_retention_duration = "604800s"
  ack_deadline_seconds       = 60

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 5
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}

# Topic 3: Energy sensor data
resource "google_pubsub_topic" "energy_data" {
  name    = "energy-data-topic"
  project = var.project_id
  labels  = var.labels

  message_retention_duration = "86600s"
}

resource "google_pubsub_subscription" "energy_data_sub" {
  name    = "energy-data-subscription"
  topic   = google_pubsub_topic.energy_data.name
  project = var.project_id
  labels  = var.labels

  message_retention_duration = "604800s"
  ack_deadline_seconds       = 60

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 5
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}

# Topic 4: Citizen app events (pothole reports, complaints etc)
resource "google_pubsub_topic" "citizen_events" {
  name    = "citizen-events-topic"
  project = var.project_id
  labels  = var.labels

  message_retention_duration = "86600s"
}

resource "google_pubsub_subscription" "citizen_events_sub" {
  name    = "citizen-events-subscription"
  topic   = google_pubsub_topic.citizen_events.name
  project = var.project_id
  labels  = var.labels

  message_retention_duration = "604800s"
  ack_deadline_seconds       = 60
}

# Dead Letter Topic
# When a message fails 5 times it lands here
# This is a production best practice - failed messages are never lost
resource "google_pubsub_topic" "dead_letter" {
  name    = "dead-letter-topic"
  project = var.project_id
  labels  = var.labels

  message_retention_duration = "604800s"
}

resource "google_pubsub_subscription" "dead_letter_sub" {
  name    = "dead-letter-subscription"
  topic   = google_pubsub_topic.dead_letter.name
  project = var.project_id
  labels  = var.labels

  message_retention_duration = "604800s"
  ack_deadline_seconds       = 60
}