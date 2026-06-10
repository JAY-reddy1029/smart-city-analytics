# =============================================================================
# Smart City Analytics — Sensor Data Generators
# =============================================================================

import random
import uuid
from datetime import datetime, timezone
from config import (
    ZONES, SENSORS_PER_ZONE,
    TRAFFIC_CONFIG, AIR_QUALITY_CONFIG, ENERGY_CONFIG
)


def get_sensor_id(sensor_type, zone, sensor_num):
    """
    Generate a consistent sensor ID.
    Format: TYPE-ZONE-NUM  e.g. TRF-zone-01-hitech-city-001
    """
    prefix = {
        "traffic":     "TRF",
        "air_quality": "AQI",
        "energy":      "ENR"
    }
    return f"{prefix[sensor_type]}-{zone}-{sensor_num:03d}"


def is_peak_hour():
    """Check if current time is peak traffic hour."""
    current_hour = datetime.now().hour
    return current_hour in TRAFFIC_CONFIG["peak_hours"]


def generate_traffic_reading(zone, sensor_num):
    """
    Generate a realistic traffic sensor reading.
    During peak hours: more vehicles, lower speed, higher congestion.
    During normal hours: fewer vehicles, higher speed.
    """
    sensor_id = get_sensor_id("traffic", zone, sensor_num)
    peak = is_peak_hour()

    # Add randomness to make data feel real
    if peak:
        vehicle_count = random.randint(
            TRAFFIC_CONFIG["peak_vehicles"] // 2,
            TRAFFIC_CONFIG["peak_vehicles"]
        )
        avg_speed = random.uniform(
            TRAFFIC_CONFIG["peak_speed"],
            TRAFFIC_CONFIG["peak_speed"] * 2
        )
    else:
        vehicle_count = random.randint(
            10,
            TRAFFIC_CONFIG["max_vehicles"]
        )
        avg_speed = random.uniform(
            TRAFFIC_CONFIG["normal_speed"] * 0.7,
            TRAFFIC_CONFIG["normal_speed"] * 1.3
        )

    # Determine congestion level based on vehicle count
    if vehicle_count > 250:
        congestion = "HIGH"
    elif vehicle_count > 150:
        congestion = "MEDIUM"
    else:
        congestion = "LOW"

    return {
        "sensor_id":        sensor_id,
        "zone_id":          zone,
        "timestamp":        datetime.now(timezone.utc).isoformat(),
        "vehicle_count":    vehicle_count,
        "avg_speed_kmh":    round(avg_speed, 2),
        "congestion_level": congestion,
        "ingested_at":      datetime.now(timezone.utc).isoformat(),
        "source":           "simulator"
    }


def generate_air_quality_reading(zone, sensor_num):
    """
    Generate a realistic air quality reading.
    Pollution levels are higher during peak traffic hours
    and vary by zone (industrial vs residential).
    """
    sensor_id = get_sensor_id("air_quality", zone, sensor_num)
    peak = is_peak_hour()

    # Industrial zones have higher pollution baseline
    industrial_zones = [
        "zone-07-kukatpally",
        "zone-08-secunderabad"
    ]
    pollution_multiplier = 1.5 if zone in industrial_zones else 1.0

    if peak:
        co2_ppm = random.uniform(
            AIR_QUALITY_CONFIG["peak_co2_ppm"] * 0.7,
            AIR_QUALITY_CONFIG["peak_co2_ppm"]
        ) * pollution_multiplier
        pm25 = random.uniform(
            AIR_QUALITY_CONFIG["peak_pm25"] * 0.5,
            AIR_QUALITY_CONFIG["peak_pm25"]
        ) * pollution_multiplier
    else:
        co2_ppm = random.uniform(
            AIR_QUALITY_CONFIG["base_co2_ppm"],
            AIR_QUALITY_CONFIG["base_co2_ppm"] * 1.5
        ) * pollution_multiplier
        pm25 = random.uniform(
            AIR_QUALITY_CONFIG["base_pm25"],
            AIR_QUALITY_CONFIG["base_pm25"] * 2
        ) * pollution_multiplier

    # Calculate AQI score from PM2.5 (simplified formula)
    if pm25 <= 12:
        aqi = int(pm25 * 4.17)           # Good
    elif pm25 <= 35.4:
        aqi = int(50 + (pm25 - 12) * 2.1)  # Moderate
    elif pm25 <= 55.4:
        aqi = int(100 + (pm25 - 35.4) * 0.5)  # Unhealthy for sensitive
    else:
        aqi = int(150 + (pm25 - 55.4) * 0.5)  # Unhealthy

    temperature = random.uniform(
        AIR_QUALITY_CONFIG["base_temp_c"],
        AIR_QUALITY_CONFIG["peak_temp_c"]
    )
    humidity = random.uniform(
        AIR_QUALITY_CONFIG["base_humidity"],
        AIR_QUALITY_CONFIG["peak_humidity"]
    )

    return {
        "sensor_id":    sensor_id,
        "zone_id":      zone,
        "timestamp":    datetime.now(timezone.utc).isoformat(),
        "co2_ppm":      round(co2_ppm, 2),
        "pm25_ugm3":    round(pm25, 2),
        "aqi_score":    aqi,
        "temperature_c": round(temperature, 2),
        "humidity_pct": round(humidity, 2),
        "ingested_at":  datetime.now(timezone.utc).isoformat(),
        "source":       "simulator"
    }


def generate_energy_reading(zone, sensor_num):
    """
    Generate a realistic energy meter reading.
    Consumption is higher during business hours and summer.
    """
    sensor_id = get_sensor_id("energy", zone, sensor_num)
    current_hour = datetime.now().hour

    # Business hours: 9 AM to 6 PM
    business_hours = range(9, 18)
    is_business = current_hour in business_hours

    if is_business:
        consumption = random.uniform(
            ENERGY_CONFIG["peak_consumption"] * 0.6,
            ENERGY_CONFIG["peak_consumption"]
        )
    else:
        consumption = random.uniform(
            ENERGY_CONFIG["base_consumption"],
            ENERGY_CONFIG["base_consumption"] * 3
        )

    voltage = random.uniform(
        ENERGY_CONFIG["base_voltage"] - ENERGY_CONFIG["voltage_variance"],
        ENERGY_CONFIG["base_voltage"] + ENERGY_CONFIG["voltage_variance"]
    )

    power_factor = random.uniform(
        ENERGY_CONFIG["min_power_factor"],
        ENERGY_CONFIG["base_power_factor"]
    )

    return {
        "sensor_id":        sensor_id,
        "zone_id":          zone,
        "timestamp":        datetime.now(timezone.utc).isoformat(),
        "consumption_kwh":  round(consumption, 3),
        "voltage_v":        round(voltage, 2),
        "power_factor":     round(power_factor, 3),
        "ingested_at":      datetime.now(timezone.utc).isoformat(),
        "source":           "simulator"
    }


def generate_all_readings():
    """
    Generate one reading from every sensor in every zone.
    Returns three lists: traffic, air_quality, energy readings.
    """
    traffic_readings     = []
    air_quality_readings = []
    energy_readings      = []

    for zone in ZONES:
        # Traffic sensors
        for i in range(1, SENSORS_PER_ZONE["traffic"] + 1):
            traffic_readings.append(
                generate_traffic_reading(zone, i)
            )

        # Air quality sensors
        for i in range(1, SENSORS_PER_ZONE["air_quality"] + 1):
            air_quality_readings.append(
                generate_air_quality_reading(zone, i)
            )

        # Energy meters
        for i in range(1, SENSORS_PER_ZONE["energy"] + 1):
            energy_readings.append(
                generate_energy_reading(zone, i)
            )

    return traffic_readings, air_quality_readings, energy_readings