# =============================================================================
# Smart City Analytics — BigQuery Service
# =============================================================================

import logging
from google.cloud import bigquery
from config import PROJECT_ID, BIGQUERY_TABLES

logger = logging.getLogger(__name__)
client = bigquery.Client(project=PROJECT_ID)


def get_traffic_hourly(zone_id: str = None, limit: int = 100):
    """Get hourly traffic summary."""
    where = f"WHERE zone_id = '{zone_id}'" if zone_id else ""
    query = f"""
        SELECT
            zone_id,
            CAST(date AS STRING)    AS date,
            hour_of_day,
            is_peak_hour,
            avg_vehicle_count,
            avg_speed_kmh,
            dominant_congestion
        FROM `{BIGQUERY_TABLES['traffic_hourly']}`
        {where}
        ORDER BY date DESC, hour_of_day DESC
        LIMIT {limit}
    """
    try:
        rows = list(client.query(query).result())
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"BigQuery error: {e}")
        return []


def get_air_quality_daily(zone_id: str = None, limit: int = 50):
    """Get daily air quality summary."""
    where = f"WHERE zone_id = '{zone_id}'" if zone_id else ""
    query = f"""
        SELECT
            zone_id,
            CAST(date AS STRING)    AS date,
            avg_aqi_score,
            max_aqi_score,
            avg_co2_ppm,
            avg_pm25_ugm3,
            daily_aqi_category,
            alert_hours
        FROM `{BIGQUERY_TABLES['air_quality_daily']}`
        {where}
        ORDER BY date DESC
        LIMIT {limit}
    """
    try:
        rows = list(client.query(query).result())
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"BigQuery error: {e}")
        return []


def get_energy_daily(zone_id: str = None, limit: int = 50):
    """Get daily energy consumption summary."""
    where = f"WHERE zone_id = '{zone_id}'" if zone_id else ""
    query = f"""
        SELECT
            zone_id,
            CAST(date AS STRING)        AS date,
            total_consumption_kwh,
            avg_voltage_v,
            high_consumption_events
        FROM `{BIGQUERY_TABLES['energy_daily']}`
        {where}
        ORDER BY date DESC
        LIMIT {limit}
    """
    try:
        rows = list(client.query(query).result())
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"BigQuery error: {e}")
        return []


def get_traffic_predictions(zone_id: str = None):
    """Get ML traffic predictions."""
    where = f"WHERE zone_id = '{zone_id}'" if zone_id else ""
    query = f"""
        SELECT
            zone_id,
            hour_of_day,
            is_peak_hour,
            avg_vehicle_count,
            predicted_will_be_high_congestion
        FROM `{BIGQUERY_TABLES['predictions']}`
        {where}
        ORDER BY hour_of_day
    """
    try:
        rows = list(client.query(query).result())
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"BigQuery error: {e}")
        return []