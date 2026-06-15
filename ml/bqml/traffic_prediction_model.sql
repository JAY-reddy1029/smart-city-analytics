-- =============================================================================
-- Smart City Analytics — BigQuery ML Traffic Prediction Model
-- =============================================================================
-- Predicts whether a zone will have HIGH congestion
-- given the hour, day of week, and historical patterns
--
-- Model type: Logistic Regression (binary classification)
-- Input:  zone_id, hour_of_day, day_of_week, avg_vehicle_count
-- Output: will_be_high_congestion (TRUE/FALSE)
-- =============================================================================

-- Step 1: Create the ML model
CREATE OR REPLACE MODEL `smart-city-analytics.ml_layer.traffic_congestion_model`
OPTIONS(
    model_type         = 'logistic_reg',
    input_label_cols   = ['will_be_high_congestion'],
    max_iterations     = 20,
    learn_rate         = 0.1,
    l2_reg             = 0.1,
    data_split_method  = 'AUTO_SPLIT'
) AS
SELECT
    zone_id,
    hour_of_day,
    day_of_week,
    is_peak_hour,
    avg_vehicle_count,
    avg_speed_kmh,
    avg_congestion_score,
    -- Label: 1 if dominant congestion is HIGH, 0 otherwise
    CASE
        WHEN dominant_congestion = 'HIGH' THEN TRUE
        ELSE FALSE
    END AS will_be_high_congestion
FROM `smart-city-analytics.analytics_layer.traffic_hourly_summary`
WHERE
    avg_vehicle_count IS NOT NULL
    AND avg_speed_kmh  IS NOT NULL
    AND dominant_congestion IS NOT NULL;