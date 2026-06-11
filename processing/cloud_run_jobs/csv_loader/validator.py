# =============================================================================
# Smart City Analytics — CSV Data Validator
# =============================================================================

import logging
import pandas as pd

logger = logging.getLogger(__name__)

VALID_CONGESTION_LEVELS = {"LOW", "MEDIUM", "HIGH"}
VALID_SOURCES           = {"batch", "simulator", "api"}
MAX_VEHICLE_COUNT       = 1000
MAX_SPEED_KMH           = 200

REQUIRED_COLUMNS = {
    "traffic": [
        "sensor_id", "zone_id", "timestamp",
        "vehicle_count", "avg_speed_kmh",
        "congestion_level", "source"
    ]
}


def validate_traffic_csv(df):
    """
    Validates a traffic CSV dataframe.
    Returns (valid_df, invalid_df, summary)
    """
    logger.info(f"Validating {len(df)} traffic records")

    valid_mask   = pd.Series([True] * len(df), index=df.index)
    error_column = pd.Series([""] * len(df), index=df.index)

    # Check required columns exist
    missing_cols = [
        col for col in REQUIRED_COLUMNS["traffic"]
        if col not in df.columns
    ]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Validate vehicle_count
    invalid_vc = ~df["vehicle_count"].between(0, MAX_VEHICLE_COUNT)
    valid_mask[invalid_vc] = False
    error_column[invalid_vc] += "invalid vehicle_count; "

    # Validate avg_speed_kmh
    invalid_speed = ~df["avg_speed_kmh"].between(0, MAX_SPEED_KMH)
    valid_mask[invalid_speed] = False
    error_column[invalid_speed] += "invalid avg_speed_kmh; "

    # Validate congestion_level
    invalid_cong = ~df["congestion_level"].isin(VALID_CONGESTION_LEVELS)
    valid_mask[invalid_cong] = False
    error_column[invalid_cong] += "invalid congestion_level; "

    # Validate source
    invalid_src = ~df["source"].isin(VALID_SOURCES)
    valid_mask[invalid_src] = False
    error_column[invalid_src] += "invalid source; "

    # Split into valid and invalid
    valid_df   = df[valid_mask].copy()
    invalid_df = df[~valid_mask].copy()

    if len(invalid_df) > 0:
        invalid_df["error"] = error_column[~valid_mask]

    summary = {
        "total":   len(df),
        "valid":   len(valid_df),
        "invalid": len(invalid_df)
    }

    logger.info(
        f"Validation complete: {summary['valid']} valid, "
        f"{summary['invalid']} invalid"
    )

    return valid_df, invalid_df, summary