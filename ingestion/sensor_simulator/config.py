# =============================================================================
# Smart City Analytics — Sensor Simulator Configuration
# =============================================================================

# GCP Project ID
PROJECT_ID = "smart-city-analytics"

# Pub/Sub topic names (must match what Terraform created)
TOPICS = {
    "traffic":     "traffic-data-topic",
    "air_quality": "air-quality-data-topic",
    "energy":      "energy-data-topic"
}

# 10 city zones
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

# Number of sensors per zone per type
SENSORS_PER_ZONE = {
    "traffic":     3,   # 3 traffic sensors per zone (main roads)
    "air_quality": 2,   # 2 air quality monitors per zone
    "energy":      4    # 4 energy meters per zone (buildings)
}

# How often each sensor type publishes data (in seconds)
PUBLISH_INTERVAL = {
    "traffic":     5,   # every 5 seconds
    "air_quality": 30,  # every 30 seconds
    "energy":      60   # every 60 seconds
}

# Batch size — how many messages to publish at once
BATCH_SIZE = 10

# Realistic data ranges for Hyderabad climate and traffic
TRAFFIC_CONFIG = {
    "peak_hours":     [8, 9, 17, 18, 19],   # morning and evening rush
    "normal_speed":   45,                    # avg speed in kmh
    "peak_speed":     15,                    # speed during rush hour
    "max_vehicles":   150,                   # max vehicles per reading
    "peak_vehicles":  300                    # vehicles during rush hour
}

AIR_QUALITY_CONFIG = {
    "base_co2_ppm":       400,    # normal CO2 level
    "peak_co2_ppm":       800,    # CO2 during high traffic
    "base_pm25":          25,     # normal PM2.5 (micrograms/m3)
    "peak_pm25":          150,    # PM2.5 during pollution event
    "base_temp_c":        28,     # normal temperature Hyderabad
    "peak_temp_c":        42,     # max temperature
    "base_humidity":      40,     # normal humidity %
    "peak_humidity":      90      # monsoon humidity %
}

ENERGY_CONFIG = {
    "base_consumption":   5.0,    # base kWh per reading
    "peak_consumption":   25.0,   # peak kWh (AC heavy usage)
    "base_voltage":       220,    # normal voltage
    "voltage_variance":   10,     # voltage fluctuation
    "base_power_factor":  0.85,   # normal power factor
    "min_power_factor":   0.70    # minimum power factor
}