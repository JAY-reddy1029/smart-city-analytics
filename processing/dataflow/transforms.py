# =============================================================================
# Smart City Analytics — Dataflow Transform Functions
# =============================================================================
# These are the building blocks of the pipeline.
# Each function does one thing — this is the Unix philosophy applied to data.
# =============================================================================

import json
import logging
from datetime import datetime, timezone

import apache_beam as beam

logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================
VALID_CONGESTION_LEVELS = {"LOW", "MEDIUM", "HIGH"}
VALID_SOURCES           = {"simulator", "api", "batch"}
MAX_VEHICLE_COUNT       = 1000
MAX_SPEED_KMH           = 200
MAX_AQI_SCORE           = 500
MAX_CO2_PPM             = 5000
MAX_PM25                = 500
MAX_CONSUMPTION_KWH     = 1000
MAX_VOLTAGE             = 260
MIN_VOLTAGE             = 180


# =============================================================================
# Step 1: Parse raw Pub/Sub message bytes → Python dict
# =============================================================================
class ParseMessage(beam.DoFn):
    """
    Reads raw bytes from Pub/Sub and converts to Python dict.
    If the message is not valid JSON, sends to dead letter.

    This is the first step — if we can't even parse it, nothing else matters.
    """

    def process(self, element):
        try:
            # Pub/Sub messages arrive as bytes — decode to string first
            if isinstance(element, bytes):
                message_str = element.decode("utf-8")
            else:
                message_str = element

            # Parse JSON string to Python dict
            data = json.loads(message_str)
            yield data

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Failed to parse message: {e} | Raw: {element}")
            yield beam.pvalue.TaggedOutput(
                "dead_letter",
                {
                    "raw_message": str(element),
                    "error":       str(e),
                    "failed_at":   datetime.now(timezone.utc).isoformat(),
                    "stage":       "parse"
                }
            )


# =============================================================================
# Step 2a: Validate traffic readings
# =============================================================================
class ValidateTrafficReading(beam.DoFn):
    """
    Validates a traffic sensor reading.
    Valid readings → main output
    Invalid readings → dead_letter output

    We never drop bad data — we route it to dead letter for investigation.
    """

    def process(self, element):
        errors = []

        # Check required fields exist
        required = [
            "sensor_id", "zone_id", "timestamp",
            "vehicle_count", "avg_speed_kmh",
            "congestion_level", "source"
        ]
        for field in required:
            if field not in element:
                errors.append(f"Missing field: {field}")

        if not errors:
            # Validate field values
            if not isinstance(element.get("vehicle_count"), int):
                errors.append("vehicle_count must be integer")
            elif not (0 <= element["vehicle_count"] <= MAX_VEHICLE_COUNT):
                errors.append(
                    f"vehicle_count out of range: "
                    f"{element['vehicle_count']}"
                )

            if not isinstance(element.get("avg_speed_kmh"), (int, float)):
                errors.append("avg_speed_kmh must be numeric")
            elif not (0 <= element["avg_speed_kmh"] <= MAX_SPEED_KMH):
                errors.append(
                    f"avg_speed_kmh out of range: "
                    f"{element['avg_speed_kmh']}"
                )

            if element.get("congestion_level") not in VALID_CONGESTION_LEVELS:
                errors.append(
                    f"Invalid congestion_level: "
                    f"{element.get('congestion_level')}"
                )

            if element.get("source") not in VALID_SOURCES:
                errors.append(f"Invalid source: {element.get('source')}")

        if errors:
            logger.warning(
                f"Invalid traffic reading: {errors} | Data: {element}"
            )
            yield beam.pvalue.TaggedOutput(
                "dead_letter",
                {
                    "raw_message": json.dumps(element),
                    "error":       "; ".join(errors),
                    "failed_at":   datetime.now(timezone.utc).isoformat(),
                    "stage":       "validate_traffic"
                }
            )
        else:
            yield element


# =============================================================================
# Step 2b: Validate air quality readings
# =============================================================================
class ValidateAirQualityReading(beam.DoFn):
    """Validates an air quality sensor reading."""

    def process(self, element):
        errors = []

        required = [
            "sensor_id", "zone_id", "timestamp",
            "co2_ppm", "pm25_ugm3", "aqi_score",
            "temperature_c", "humidity_pct", "source"
        ]
        for field in required:
            if field not in element:
                errors.append(f"Missing field: {field}")

        if not errors:
            if not (0 <= element.get("co2_ppm", -1) <= MAX_CO2_PPM):
                errors.append(f"co2_ppm out of range: {element.get('co2_ppm')}")

            if not (0 <= element.get("pm25_ugm3", -1) <= MAX_PM25):
                errors.append(
                    f"pm25_ugm3 out of range: {element.get('pm25_ugm3')}"
                )

            if not (0 <= element.get("aqi_score", -1) <= MAX_AQI_SCORE):
                errors.append(
                    f"aqi_score out of range: {element.get('aqi_score')}"
                )

            if not (-10 <= element.get("temperature_c", -999) <= 60):
                errors.append(
                    f"temperature_c out of range: "
                    f"{element.get('temperature_c')}"
                )

            if not (0 <= element.get("humidity_pct", -1) <= 100):
                errors.append(
                    f"humidity_pct out of range: "
                    f"{element.get('humidity_pct')}"
                )

        if errors:
            logger.warning(
                f"Invalid air quality reading: {errors} | Data: {element}"
            )
            yield beam.pvalue.TaggedOutput(
                "dead_letter",
                {
                    "raw_message": json.dumps(element),
                    "error":       "; ".join(errors),
                    "failed_at":   datetime.now(timezone.utc).isoformat(),
                    "stage":       "validate_air_quality"
                }
            )
        else:
            yield element


# =============================================================================
# Step 2c: Validate energy readings
# =============================================================================
class ValidateEnergyReading(beam.DoFn):
    """Validates an energy meter reading."""

    def process(self, element):
        errors = []

        required = [
            "sensor_id", "zone_id", "timestamp",
            "consumption_kwh", "voltage_v",
            "power_factor", "source"
        ]
        for field in required:
            if field not in element:
                errors.append(f"Missing field: {field}")

        if not errors:
            if not (0 <= element.get("consumption_kwh", -1) <= MAX_CONSUMPTION_KWH):
                errors.append(
                    f"consumption_kwh out of range: "
                    f"{element.get('consumption_kwh')}"
                )

            if not (MIN_VOLTAGE <= element.get("voltage_v", 0) <= MAX_VOLTAGE):
                errors.append(
                    f"voltage_v out of range: {element.get('voltage_v')}"
                )

            if not (0 <= element.get("power_factor", -1) <= 1):
                errors.append(
                    f"power_factor out of range: "
                    f"{element.get('power_factor')}"
                )

        if errors:
            logger.warning(
                f"Invalid energy reading: {errors} | Data: {element}"
            )
            yield beam.pvalue.TaggedOutput(
                "dead_letter",
                {
                    "raw_message": json.dumps(element),
                    "error":       "; ".join(errors),
                    "failed_at":   datetime.now(timezone.utc).isoformat(),
                    "stage":       "validate_energy"
                }
            )
        else:
            yield element


# =============================================================================
# Step 3: Add pipeline metadata to each record
# =============================================================================
class EnrichRecord(beam.DoFn):
    """
    Adds pipeline metadata to each record before writing to BigQuery.
    This is important for data lineage — you can always tell
    which pipeline run processed a record and when.
    """

    def __init__(self, pipeline_name):
        self.pipeline_name = pipeline_name

    def process(self, element):
        element["ingested_at"] = datetime.now(timezone.utc).isoformat()
        yield element


# =============================================================================
# BigQuery table schemas
# Used by Dataflow to write data correctly
# =============================================================================
TRAFFIC_SCHEMA = {
    "fields": [
        {"name": "sensor_id",        "type": "STRING",    "mode": "REQUIRED"},
        {"name": "zone_id",          "type": "STRING",    "mode": "REQUIRED"},
        {"name": "timestamp",        "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "vehicle_count",    "type": "INTEGER",   "mode": "NULLABLE"},
        {"name": "avg_speed_kmh",    "type": "FLOAT",     "mode": "NULLABLE"},
        {"name": "congestion_level", "type": "STRING",    "mode": "NULLABLE"},
        {"name": "ingested_at",      "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "source",           "type": "STRING",    "mode": "REQUIRED"},
    ]
}

AIR_QUALITY_SCHEMA = {
    "fields": [
        {"name": "sensor_id",     "type": "STRING",    "mode": "REQUIRED"},
        {"name": "zone_id",       "type": "STRING",    "mode": "REQUIRED"},
        {"name": "timestamp",     "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "co2_ppm",       "type": "FLOAT",     "mode": "NULLABLE"},
        {"name": "pm25_ugm3",     "type": "FLOAT",     "mode": "NULLABLE"},
        {"name": "aqi_score",     "type": "INTEGER",   "mode": "NULLABLE"},
        {"name": "temperature_c", "type": "FLOAT",     "mode": "NULLABLE"},
        {"name": "humidity_pct",  "type": "FLOAT",     "mode": "NULLABLE"},
        {"name": "ingested_at",   "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "source",        "type": "STRING",    "mode": "REQUIRED"},
    ]
}

ENERGY_SCHEMA = {
    "fields": [
        {"name": "sensor_id",       "type": "STRING",    "mode": "REQUIRED"},
        {"name": "zone_id",         "type": "STRING",    "mode": "REQUIRED"},
        {"name": "timestamp",       "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "consumption_kwh", "type": "FLOAT",     "mode": "NULLABLE"},
        {"name": "voltage_v",       "type": "FLOAT",     "mode": "NULLABLE"},
        {"name": "power_factor",    "type": "FLOAT",     "mode": "NULLABLE"},
        {"name": "ingested_at",     "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "source",          "type": "STRING",    "mode": "REQUIRED"},
    ]
}

DEAD_LETTER_SCHEMA = {
    "fields": [
        {"name": "raw_message", "type": "STRING",    "mode": "REQUIRED"},
        {"name": "error",       "type": "STRING",    "mode": "REQUIRED"},
        {"name": "failed_at",   "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "stage",       "type": "STRING",    "mode": "REQUIRED"},
    ]
}