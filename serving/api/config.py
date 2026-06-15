# =============================================================================
# Smart City Analytics — API Configuration
# =============================================================================

PROJECT_ID       = "smart-city-analytics"
BIGTABLE_INSTANCE = "smart-city-bigtable"

BIGQUERY_TABLES = {
    "traffic_hourly":    "smart-city-analytics.analytics_layer.traffic_hourly_summary",
    "air_quality_daily": "smart-city-analytics.analytics_layer.zone_air_quality_daily",
    "energy_daily":      "smart-city-analytics.analytics_layer.city_energy_daily",
    "predictions":       "smart-city-analytics.ml_layer.traffic_predictions"
}

BIGTABLE_TABLES = {
    "traffic":     "traffic_latest",
    "air_quality": "air_quality_latest",
    "energy":      "energy_latest"
}

API_TITLE       = "Smart City Analytics API"
API_VERSION     = "1.0.0"
API_DESCRIPTION = """
Production REST API for Smart City Analytics Platform.

## Features
- Real-time sensor readings from Bigtable
- Historical analytics from BigQuery
- ML-powered traffic congestion predictions
- Air quality monitoring and alerts
"""