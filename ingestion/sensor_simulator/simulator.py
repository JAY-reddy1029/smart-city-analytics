# =============================================================================
# Smart City Analytics — Main Sensor Simulator
# =============================================================================

import json
import time
import logging
import signal
import sys
from datetime import datetime
from concurrent.futures import TimeoutError

from google.cloud import pubsub_v1
from google.api_core.exceptions import GoogleAPIError

from config import PROJECT_ID, TOPICS, PUBLISH_INTERVAL, BATCH_SIZE
from sensors import generate_all_readings

# =============================================================================
# Logging setup — structured logging like real production systems
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# =============================================================================
# Publisher setup
# =============================================================================
def create_publisher():
    """
    Create a Pub/Sub publisher with batching enabled.
    Batching = collect multiple messages and send them together.
    More efficient than sending one message at a time.
    """
    batch_settings = pubsub_v1.types.BatchSettings(
        max_messages=BATCH_SIZE,
        max_bytes=1024 * 1024,   # 1 MB max batch size
        max_latency=0.1          # wait max 100ms before sending batch
    )
    return pubsub_v1.PublisherClient(batch_settings=batch_settings)


def get_topic_path(publisher, topic_name):
    """Build the full Pub/Sub topic path."""
    return publisher.topic_path(PROJECT_ID, topic_name)


# =============================================================================
# Publishing functions
# =============================================================================
def publish_message(publisher, topic_path, data):
    """
    Publish a single message to Pub/Sub.
    Messages must be bytes, so we convert dict → JSON → bytes.
    """
    try:
        message_bytes = json.dumps(data).encode("utf-8")
        future = publisher.publish(topic_path, message_bytes)
        return future
    except Exception as e:
        logger.error(f"Failed to publish message: {e}")
        return None


def publish_batch(publisher, topic_path, readings, sensor_type):
    """
    Publish a batch of sensor readings to a Pub/Sub topic.
    Returns count of successfully published messages.
    """
    futures = []
    for reading in readings:
        future = publish_message(publisher, topic_path, reading)
        if future:
            futures.append(future)

    # Wait for all messages to be confirmed by Pub/Sub
    success_count = 0
    for future in futures:
        try:
            message_id = future.result(timeout=30)
            success_count += 1
        except TimeoutError:
            logger.error("Pub/Sub publish timeout")
        except GoogleAPIError as e:
            logger.error(f"Pub/Sub API error: {e}")

    logger.info(
        f"Published {success_count}/{len(readings)} "
        f"{sensor_type} readings"
    )
    return success_count


# =============================================================================
# Stats tracking
# =============================================================================
class SimulatorStats:
    """Track publishing statistics for monitoring."""

    def __init__(self):
        self.total_published  = 0
        self.total_errors     = 0
        self.start_time       = datetime.now()
        self.counts = {
            "traffic":     0,
            "air_quality": 0,
            "energy":      0
        }

    def update(self, sensor_type, count):
        self.total_published    += count
        self.counts[sensor_type] += count

    def log_summary(self):
        elapsed = (datetime.now() - self.start_time).seconds
        logger.info(
            f"STATS | "
            f"Total published: {self.total_published} | "
            f"Traffic: {self.counts['traffic']} | "
            f"AirQuality: {self.counts['air_quality']} | "
            f"Energy: {self.counts['energy']} | "
            f"Runtime: {elapsed}s"
        )


# =============================================================================
# Main simulator loop
# =============================================================================
def run_simulator():
    """
    Main simulator loop.
    Publishes sensor data continuously until stopped.
    Press Ctrl+C to stop gracefully.
    """
    logger.info("=" * 60)
    logger.info("Smart City Analytics — Sensor Simulator Starting")
    logger.info(f"Project: {PROJECT_ID}")
    logger.info(f"Topics:  {list(TOPICS.values())}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)

    # Create publisher
    publisher = create_publisher()

    # Build topic paths
    topic_paths = {
        sensor_type: get_topic_path(publisher, topic_name)
        for sensor_type, topic_name in TOPICS.items()
    }

    # Stats tracker
    stats = SimulatorStats()

    # Graceful shutdown on Ctrl+C
    def handle_shutdown(signum, frame):
        logger.info("Shutdown signal received. Stopping simulator...")
        stats.log_summary()
        logger.info("Simulator stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Counters for interval management
    cycle         = 0
    stats_every   = 10  # print stats every 10 cycles

    logger.info("Starting data generation...")

    while True:
        cycle += 1
        cycle_start = time.time()

        # Generate readings from all sensors
        traffic_readings, air_quality_readings, energy_readings = (
            generate_all_readings()
        )

        # Always publish traffic (every 5 seconds)
        count = publish_batch(
            publisher,
            topic_paths["traffic"],
            traffic_readings,
            "traffic"
        )
        stats.update("traffic", count)

        # Publish air quality every 6 cycles (30 seconds)
        if cycle % 6 == 0:
            count = publish_batch(
                publisher,
                topic_paths["air_quality"],
                air_quality_readings,
                "air_quality"
            )
            stats.update("air_quality", count)

        # Publish energy every 12 cycles (60 seconds)
        if cycle % 12 == 0:
            count = publish_batch(
                publisher,
                topic_paths["energy"],
                energy_readings,
                "energy"
            )
            stats.update("energy", count)

        # Print stats summary every 10 cycles
        if cycle % stats_every == 0:
            stats.log_summary()

        # Wait before next cycle
        elapsed = time.time() - cycle_start
        sleep_time = max(0, PUBLISH_INTERVAL["traffic"] - elapsed)
        time.sleep(sleep_time)


# =============================================================================
# Entry point
# =============================================================================
if __name__ == "__main__":
    run_simulator()