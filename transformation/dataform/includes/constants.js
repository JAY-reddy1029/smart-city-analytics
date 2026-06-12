// =============================================================================
// Smart City Analytics — Shared Constants
// =============================================================================

const PROJECT_ID    = "smart-city-analytics";
const RAW_DATASET   = "raw_layer";
const SILVER_DATASET = "processed_layer";
const GOLD_DATASET  = "analytics_layer";

const VALID_CONGESTION_LEVELS = ["LOW", "MEDIUM", "HIGH"];
const VALID_ZONES = [
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
];

module.exports = {
    PROJECT_ID,
    RAW_DATASET,
    SILVER_DATASET,
    GOLD_DATASET,
    VALID_CONGESTION_LEVELS,
    VALID_ZONES
};