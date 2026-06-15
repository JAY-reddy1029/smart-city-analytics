# =============================================================================
# Smart City Analytics — FastAPI REST API
# =============================================================================

import logging
from datetime import datetime, timezone
from typing   import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from config           import API_TITLE, API_VERSION, API_DESCRIPTION
from models           import HealthResponse, APIResponse
from bigquery_service import (
    get_traffic_hourly,
    get_air_quality_daily,
    get_energy_daily,
    get_traffic_predictions
)

# =============================================================================
# Logging
# =============================================================================
logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# =============================================================================
# FastAPI app
# =============================================================================
app = FastAPI(
    title       = API_TITLE,
    version     = API_VERSION,
    description = API_DESCRIPTION
)

# Allow all origins for now (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"]
)


# =============================================================================
# Health check
# =============================================================================
@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint — used by Cloud Run to verify the service is up."""
    return HealthResponse(
        status    = "healthy",
        timestamp = datetime.now(timezone.utc).isoformat(),
        version   = API_VERSION
    )


# =============================================================================
# Traffic endpoints
# =============================================================================
@app.get("/traffic/hourly")
def traffic_hourly(
    zone_id: Optional[str] = Query(None, description="Filter by zone ID"),
    limit:   int           = Query(100,  description="Max records to return")
):
    """Get hourly traffic summary for all zones or a specific zone."""
    logger.info(f"GET /traffic/hourly zone_id={zone_id}")
    data = get_traffic_hourly(zone_id=zone_id, limit=limit)
    return APIResponse(success=True, data=data, count=len(data))


@app.get("/traffic/hourly/{zone_id}")
def traffic_hourly_by_zone(zone_id: str):
    """Get hourly traffic summary for a specific zone."""
    logger.info(f"GET /traffic/hourly/{zone_id}")
    data = get_traffic_hourly(zone_id=zone_id, limit=50)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data for zone {zone_id}")
    return APIResponse(success=True, data=data, count=len(data))


@app.get("/traffic/predictions")
def traffic_predictions(
    zone_id: Optional[str] = Query(None, description="Filter by zone ID")
):
    """Get ML-powered traffic congestion predictions."""
    logger.info(f"GET /traffic/predictions zone_id={zone_id}")
    data = get_traffic_predictions(zone_id=zone_id)
    return APIResponse(success=True, data=data, count=len(data))


@app.get("/traffic/predictions/{zone_id}")
def traffic_predictions_by_zone(zone_id: str):
    """Get ML predictions for a specific zone."""
    logger.info(f"GET /traffic/predictions/{zone_id}")
    data = get_traffic_predictions(zone_id=zone_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"No predictions for zone {zone_id}")
    return APIResponse(success=True, data=data, count=len(data))


# =============================================================================
# Air quality endpoints
# =============================================================================
@app.get("/airquality/daily")
def air_quality_daily(
    zone_id: Optional[str] = Query(None, description="Filter by zone ID"),
    limit:   int           = Query(50,   description="Max records to return")
):
    """Get daily air quality summary."""
    logger.info(f"GET /airquality/daily zone_id={zone_id}")
    data = get_air_quality_daily(zone_id=zone_id, limit=limit)
    return APIResponse(success=True, data=data, count=len(data))


@app.get("/airquality/daily/{zone_id}")
def air_quality_by_zone(zone_id: str):
    """Get daily air quality for a specific zone."""
    logger.info(f"GET /airquality/daily/{zone_id}")
    data = get_air_quality_daily(zone_id=zone_id, limit=30)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data for zone {zone_id}")
    return APIResponse(success=True, data=data, count=len(data))


# =============================================================================
# Energy endpoints
# =============================================================================
@app.get("/energy/daily")
def energy_daily(
    zone_id: Optional[str] = Query(None, description="Filter by zone ID"),
    limit:   int           = Query(50,   description="Max records to return")
):
    """Get daily energy consumption summary."""
    logger.info(f"GET /energy/daily zone_id={zone_id}")
    data = get_energy_daily(zone_id=zone_id, limit=limit)
    return APIResponse(success=True, data=data, count=len(data))


@app.get("/energy/daily/{zone_id}")
def energy_by_zone(zone_id: str):
    """Get daily energy for a specific zone."""
    logger.info(f"GET /energy/daily/{zone_id}")
    data = get_energy_daily(zone_id=zone_id, limit=30)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data for zone {zone_id}")
    return APIResponse(success=True, data=data, count=len(data))


# =============================================================================
# Entry point
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)