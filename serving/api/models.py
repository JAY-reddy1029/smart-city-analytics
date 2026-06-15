# =============================================================================
# Smart City Analytics — API Response Models
# =============================================================================

from pydantic import BaseModel
from typing   import Optional, List
from datetime import datetime


class HealthResponse(BaseModel):
    status:    str
    timestamp: str
    version:   str


class TrafficReading(BaseModel):
    zone_id:          str
    hour_of_day:      int
    avg_vehicle_count: float
    avg_speed_kmh:    float
    dominant_congestion: str
    is_peak_hour:     bool
    date:             str


class AirQualityReading(BaseModel):
    zone_id:          str
    date:             str
    avg_aqi_score:    float
    max_aqi_score:    float
    avg_co2_ppm:      float
    avg_pm25_ugm3:    float
    daily_aqi_category: str
    alert_hours:      int


class TrafficPrediction(BaseModel):
    zone_id:                           str
    hour_of_day:                       int
    is_peak_hour:                      bool
    avg_vehicle_count:                 float
    predicted_will_be_high_congestion: bool


class EnergyReading(BaseModel):
    zone_id:               str
    date:                  str
    total_consumption_kwh: float
    avg_voltage_v:         float
    high_consumption_events: int


class APIResponse(BaseModel):
    success: bool
    data:    Optional[object] = None
    error:   Optional[str]   = None
    count:   Optional[int]   = None