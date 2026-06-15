-- =============================================================================
-- Evaluate model performance
-- =============================================================================

SELECT
    *
FROM ML.EVALUATE(
    MODEL `smart-city-analytics.ml_layer.traffic_congestion_model`
);