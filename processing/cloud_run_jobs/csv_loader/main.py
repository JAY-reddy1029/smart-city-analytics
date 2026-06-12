# =============================================================================
# Smart City Analytics — Cloud Run CSV Loader Job
# =============================================================================
# Triggered by Eventarc when a CSV file lands in GCS.
# Reads the file, validates it, loads it to BigQuery.
#
# Environment variables (set by Cloud Run):
#   BUCKET_NAME  - GCS bucket name
#   FILE_NAME    - CSV file path in bucket
#   SENSOR_TYPE  - traffic / air_quality / energy
# =============================================================================

import os
import logging
import sys
from datetime import datetime, timezone

import pandas as pd
from google.cloud import storage

from validator import validate_traffic_csv
from bigquery_writer import (
    prepare_traffic_records,
    write_to_bigquery,
    write_dead_letters
)

# =============================================================================
# Logging setup
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# =============================================================================
# GCS file reader
# =============================================================================
def read_csv_from_gcs(bucket_name, file_name):
    """
    Download CSV file from GCS and read into pandas DataFrame.
    """
    logger.info(f"Reading gs://{bucket_name}/{file_name}")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob   = bucket.blob(file_name)

    # Download as bytes and read into pandas
    content = blob.download_as_bytes()
    df      = pd.read_csv(
        pd.io.common.BytesIO(content),
        dtype={
            "sensor_id":        str,
            "zone_id":          str,
            "congestion_level": str,
            "source":           str
        }
    )

    logger.info(f"Read {len(df)} rows from {file_name}")
    return df


# =============================================================================
# Main job logic
# =============================================================================
def run():
    """
    Main Cloud Run job logic.
    Reads env vars, downloads CSV, validates, loads to BigQuery.
    """
    logger.info("=" * 60)
    logger.info("Smart City Analytics — CSV Loader Job Starting")
    logger.info("=" * 60)

    # Read environment variables
    bucket_name = os.environ.get("BUCKET_NAME")
    file_name   = os.environ.get("FILE_NAME")
    sensor_type = os.environ.get("SENSOR_TYPE", "traffic")

    # For local testing — use defaults
    if not bucket_name:
        bucket_name = "smart-city-analytics-raw-data"
        logger.info(f"BUCKET_NAME not set, using default: {bucket_name}")

    if not file_name:
        file_name = "sample_traffic_data.csv"
        logger.info(f"FILE_NAME not set, using default: {file_name}")

    logger.info(f"Processing: gs://{bucket_name}/{file_name}")
    logger.info(f"Sensor type: {sensor_type}")

    try:
        # Step 1: Read CSV from GCS
        df = read_csv_from_gcs(bucket_name, file_name)

        # Step 2: Validate data
        if sensor_type == "traffic":
            valid_df, invalid_df, summary = validate_traffic_csv(df)
            table_id = "traffic_raw"
        else:
            raise ValueError(f"Unsupported sensor type: {sensor_type}")

        logger.info(
            f"Validation summary: "
            f"{summary['valid']} valid, "
            f"{summary['invalid']} invalid "
            f"out of {summary['total']} total"
        )

        # Step 3: Write valid records to BigQuery
        if len(valid_df) > 0:
            records        = prepare_traffic_records(valid_df)
            success, errors = write_to_bigquery(records, table_id)
            logger.info(
                f"BigQuery write: {success} success, {errors} errors"
            )

        # Step 4: Write invalid records to dead letter
        if len(invalid_df) > 0:
            write_dead_letters(invalid_df, file_name)

        logger.info("=" * 60)
        logger.info("CSV Loader Job Completed Successfully")
        logger.info(f"File: {file_name}")
        logger.info(f"Valid records loaded: {summary['valid']}")
        logger.info(f"Invalid records: {summary['invalid']}")
        logger.info("=" * 60)

        sys.exit(0)

    except Exception as e:
        logger.error(f"Job failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run()