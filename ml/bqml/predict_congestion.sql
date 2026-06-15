-- =============================================================================
-- Make predictions — will each zone be congested at each hour?
-- =============================================================================

CREATE OR REPLACE TABLE `smart-city-analytics.ml_layer.traffic_predictions`
AS
SELECT
    zone_id,
    hour_of_day,
    day_of_week,
    is_peak_hour,
    avg_vehicle_count,
    predicted_will_be_high_congestion,
    predicted_will_be_high_congestion_probs
FROM ML.PREDICT(
    MODEL `smart-city-analytics.ml_layer.traffic_congestion_model`,
    (
        SELECT
            zone_id,
            hour_of_day,
            day_of_week,
            is_peak_hour,
            avg_vehicle_count,
            avg_speed_kmh,
            avg_congestion_score
        FROM `smart-city-analytics.analytics_layer.traffic_hourly_summary`
        WHERE date = (
            SELECT MAX(date)
            FROM `smart-city-analytics.analytics_layer.traffic_hourly_summary`
        )
    )
);