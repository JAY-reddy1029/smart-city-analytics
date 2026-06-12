# =============================================================================
# Smart City Analytics — Dataflow Streaming Pipeline
# =============================================================================
# Reads from Pub/Sub → Validates → Writes to BigQuery
#
# Run locally (DirectRunner) for testing:
#   python pipeline.py --runner=DirectRunner --sensor_type=traffic
#
# Run on GCP (DataflowRunner) for production:
#   python pipeline.py --runner=DataflowRunner --sensor_type=traffic
# =============================================================================

import argparse
import logging

import apache_beam as beam
from apache_beam.options.pipeline_options import (
    PipelineOptions,
    StandardOptions,
    GoogleCloudOptions,
    SetupOptions
)
from apache_beam.io.gcp.bigquery import WriteToBigQuery
from apache_beam.io.gcp.bigquery import BigQueryDisposition

from transforms import (
    ParseMessage,
    ValidateTrafficReading,
    ValidateAirQualityReading,
    ValidateEnergyReading,
    EnrichRecord,
    TRAFFIC_SCHEMA,
    AIR_QUALITY_SCHEMA,
    ENERGY_SCHEMA,
    DEAD_LETTER_SCHEMA
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# GCP Configuration
# =============================================================================
PROJECT_ID = "smart-city-analytics"
REGION     = "us-central1"
DATASET    = "raw_layer"

PUBSUB_TOPICS = {
    "traffic":     f"projects/{PROJECT_ID}/topics/traffic-data-topic",
    "air_quality": f"projects/{PROJECT_ID}/topics/air-quality-data-topic",
    "energy":      f"projects/{PROJECT_ID}/topics/energy-data-topic"
}

BIGQUERY_TABLES = {
    "traffic":     f"{PROJECT_ID}:{DATASET}.traffic_raw",
    "air_quality": f"{PROJECT_ID}:{DATASET}.air_quality_raw",
    "energy":      f"{PROJECT_ID}:{DATASET}.energy_raw",
    "dead_letter": f"{PROJECT_ID}:{DATASET}.dead_letter_raw"
}

SCHEMAS = {
    "traffic":     TRAFFIC_SCHEMA,
    "air_quality": AIR_QUALITY_SCHEMA,
    "energy":      ENERGY_SCHEMA,
    "dead_letter": DEAD_LETTER_SCHEMA
}

VALIDATORS = {
    "traffic":     ValidateTrafficReading,
    "air_quality": ValidateAirQualityReading,
    "energy":      ValidateEnergyReading
}


# =============================================================================
# Pipeline builder
# =============================================================================
def build_pipeline(pipeline, sensor_type):
    """
    Builds the Dataflow pipeline for a given sensor type.

    Flow:
    Read from Pub/Sub
        → Parse JSON
        → Validate
        → Enrich with metadata
        → Write valid records to BigQuery raw_layer
        → Write invalid records to BigQuery dead_letter
    """

    pubsub_topic = PUBSUB_TOPICS[sensor_type]
    bq_table     = BIGQUERY_TABLES[sensor_type]
    dl_table     = BIGQUERY_TABLES["dead_letter"]
    schema       = SCHEMAS[sensor_type]
    dl_schema    = SCHEMAS["dead_letter"]
    validator    = VALIDATORS[sensor_type]

    logger.info(f"Building pipeline for sensor type: {sensor_type}")
    logger.info(f"Reading from: {pubsub_topic}")
    logger.info(f"Writing to:   {bq_table}")

    # Step 1: Read from Pub/Sub
    raw_messages = (
        pipeline
        | "ReadFromPubSub" >> beam.io.ReadFromPubSub(topic=pubsub_topic)
    )

    # Step 2: Parse JSON bytes → Python dict
    parsed = (
        raw_messages
        | "ParseMessages" >> beam.ParDo(
            ParseMessage()
        ).with_outputs("dead_letter", main="valid")
    )

    # Step 3: Validate — route valid vs invalid
    validated = (
        parsed.valid
        | "ValidateReadings" >> beam.ParDo(
            validator()
        ).with_outputs("dead_letter", main="valid")
    )

    # Step 4: Enrich valid records with metadata
    enriched = (
        validated.valid
        | "EnrichRecords" >> beam.ParDo(
            EnrichRecord(pipeline_name=f"smart-city-{sensor_type}-pipeline")
        )
    )

    # Step 5: Write valid records to BigQuery
    enriched | "WriteToBigQuery" >> WriteToBigQuery(
        table=bq_table,
        schema=schema,
        write_disposition=BigQueryDisposition.WRITE_APPEND,
        create_disposition=BigQueryDisposition.CREATE_NEVER
    )

    # Step 6: Collect all dead letter records
    dead_letters = (
        (parsed.dead_letter, validated.dead_letter)
        | "MergeDeadLetters" >> beam.Flatten()
    )

    # Step 7: Write dead letter records to BigQuery
    dead_letters | "WriteDeadLetters" >> WriteToBigQuery(
        table=dl_table,
        schema=dl_schema,
        write_disposition=BigQueryDisposition.WRITE_APPEND,
        create_disposition=BigQueryDisposition.CREATE_IF_NEEDED
    )

    return pipeline


# =============================================================================
# Pipeline options and entry point
# =============================================================================
def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sensor_type",
        required=True,
        choices=["traffic", "air_quality", "energy"],
        help="Which sensor type to process"
    )
    parser.add_argument(
        "--runner",
        default="DirectRunner",
        choices=["DirectRunner", "DataflowRunner"],
        help="Pipeline runner"
    )
    known_args, pipeline_args = parser.parse_known_args(argv)

    # Pipeline options
    options = PipelineOptions(pipeline_args)
    options.view_as(SetupOptions).save_main_session = True

    # Streaming mode — required for Pub/Sub reading
    options.view_as(StandardOptions).streaming = True

    if known_args.runner == "DataflowRunner":
        gcp_options = options.view_as(GoogleCloudOptions)
        gcp_options.project  = PROJECT_ID
        gcp_options.region   = REGION
        gcp_options.job_name = (
            f"smart-city-{known_args.sensor_type}-pipeline"
        )
        gcp_options.staging_location = (
            f"gs://{PROJECT_ID}-dataflow-staging/staging"
        )
        gcp_options.temp_location = (
            f"gs://{PROJECT_ID}-dataflow-staging/temp"
        )

    logger.info(
        f"Starting pipeline | sensor_type={known_args.sensor_type} "
        f"| runner={known_args.runner}"
    )

    with beam.Pipeline(
        runner=known_args.runner,
        options=options
    ) as pipeline:
        build_pipeline(pipeline, known_args.sensor_type)

    logger.info("Pipeline completed successfully")


if __name__ == "__main__":
    run()