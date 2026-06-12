# =============================================================================
# Smart City Analytics — BigQuery Writer
# =============================================================================

import logging
from datetime import datetime, timezone

from google.cloud import bigquery

logger = logging.getLogger(__name__)

PROJECT_ID = "smart-city-analytics"
DATASET    = "raw_layer"


def get_client():
    """Create BigQuery client."""
    return bigquery.Client(project=PROJECT_ID)


def prepare_traffic_records(df):
    """
    Convert dataframe rows to BigQuery-ready dicts.
    Adds ingested_at timestamp to every record.
    """
    records    = df.to_dict("records")
    ingested_at = datetime.now(timezone.utc).isoformat()

    for record in records:
        # Convert timestamp string to proper format
        if isinstance(record.get("timestamp"), str):
            record["timestamp"] = record["timestamp"].replace(" ", "T") + "Z"

        # Ensure correct types
        record["vehicle_count"] = int(record["vehicle_count"])
        record["avg_speed_kmh"] = float(record["avg_speed_kmh"])
        record["ingested_at"]   = ingested_at

    return records


def write_to_bigquery(records, table_id):
    """
    Write records to BigQuery table.
    Uses streaming insert for immediate availability.
    Returns (success_count, error_count)
    """
    if not records:
        logger.info("No records to write")
        return 0, 0

    client = get_client()
    table_ref = f"{PROJECT_ID}.{DATASET}.{table_id}"

    logger.info(f"Writing {len(records)} records to {table_ref}")

    errors = client.insert_rows_json(table_ref, records)

    if errors:
        logger.error(f"BigQuery insert errors: {errors}")
        return len(records) - len(errors), len(errors)

    logger.info(f"Successfully wrote {len(records)} records to {table_ref}")
    return len(records), 0


def write_dead_letters(invalid_df, source_file):
    """
    Write invalid records to dead letter table for investigation.
    """
    if len(invalid_df) == 0:
        return

    client      = get_client()
    table_ref   = f"{PROJECT_ID}.{DATASET}.dead_letter_raw"
    ingested_at = datetime.now(timezone.utc).isoformat()

    records = []
    for _, row in invalid_df.iterrows():
        records.append({
            "raw_message": str(row.to_dict()),
            "error":       row.get("error", "unknown"),
            "failed_at":   ingested_at,
            "stage":       f"csv_validation:{source_file}"
        })

    errors = client.insert_rows_json(table_ref, records)
    if errors:
        logger.error(f"Dead letter write errors: {errors}")
    else:
        logger.info(
            f"Wrote {len(records)} dead letter records"
        )