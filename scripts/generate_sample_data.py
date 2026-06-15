# =============================================================================
# Smart City Analytics — Sample Data Generator
# Generates multiple days of traffic CSV files and uploads to GCS
# =============================================================================

import csv
import random
from datetime import datetime, timedelta
from google.cloud import storage

PROJECT_ID  = "smart-city-analytics"
BUCKET_NAME = "smart-city-analytics-raw-data"

ZONES = [
    "zone-01-hitech-city",
    "zone-02-banjara-hills",
    "zone-03-jubilee-hills",
    "zone-04-gachibowli",
    "zone-05-madhapur",
    "zone-06-kondapur",
    "zone-07-kukatpally",
    "zone-08-secunderabad",
    "zone-09-begumpet",
    "zone-10-ameerpet"
]

PEAK_HOURS   = [7, 8, 9, 17, 18, 19, 20]
SENSORS_PER_ZONE = 3


def get_congestion(vehicle_count):
    if vehicle_count > 200:
        return "HIGH"
    elif vehicle_count > 120:
        return "MEDIUM"
    else:
        return "LOW"


def generate_day_data(date):
    rows = []
    for zone in ZONES:
        for sensor_num in range(1, SENSORS_PER_ZONE + 1):
            sensor_id = f"TRF-{zone}-{sensor_num:03d}"
            for hour in range(6, 23):
                timestamp = datetime(
                    date.year, date.month, date.day, hour, 0, 0
                )
                is_peak = hour in PEAK_HOURS
                if is_peak:
                    vehicle_count = random.randint(180, 320)
                    avg_speed     = round(random.uniform(10, 25), 2)
                else:
                    vehicle_count = random.randint(30, 130)
                    avg_speed     = round(random.uniform(35, 65), 2)

                rows.append({
                    "sensor_id":        sensor_id,
                    "zone_id":          zone,
                    "timestamp":        timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "vehicle_count":    vehicle_count,
                    "avg_speed_kmh":    avg_speed,
                    "congestion_level": get_congestion(vehicle_count),
                    "source":           "batch"
                })
    return rows


def write_csv(rows, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "sensor_id", "zone_id", "timestamp",
            "vehicle_count", "avg_speed_kmh",
            "congestion_level", "source"
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Written {len(rows)} rows to {filename}")


def upload_to_gcs(filename, blob_name):
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob   = bucket.blob(blob_name)
    blob.upload_from_filename(filename)
    print(f"Uploaded {filename} to gs://{BUCKET_NAME}/{blob_name}")


def main():
    # Generate 30 days of data
    start_date = datetime(2026, 5, 1)
    for i in range(30):
        date     = start_date + timedelta(days=i)
        filename = f"traffic_{date.strftime('%Y_%m_%d')}.csv"
        blob_name = f"batch/{filename}"

        print(f"Generating data for {date.strftime('%Y-%m-%d')}...")
        rows = generate_day_data(date)
        write_csv(rows, filename)
        upload_to_gcs(filename, blob_name)

        # Clean up local file
        import os
        os.remove(filename)

    print("Done! 30 days of data uploaded to GCS.")


if __name__ == "__main__":
    main()