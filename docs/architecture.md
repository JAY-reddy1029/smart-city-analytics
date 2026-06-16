# Smart City Analytics Platform — Architecture Documentation

## Overview

This document explains every architectural decision made in this project —
why each service was chosen, what alternatives were considered, and what
trade-offs were made. This is the kind of thinking that separates a
data engineer from a script writer.

---

## 1. Why Pub/Sub instead of Kafka?

**Decision:** Use Google Cloud Pub/Sub for real-time message streaming.

**Alternatives considered:** Apache Kafka (on Compute Engine or Confluent Cloud)

**Why Pub/Sub:**
- Fully managed — no brokers to manage, patch, or scale
- Native integration with Dataflow, Cloud Run, Eventarc
- Auto-scales to millions of messages per second
- Free tier: 10GB/month — sufficient for this project

**Why not Kafka:**
- Requires VM management (Compute Engine) or paid managed service
- Overkill for a single-project smart city deployment
- No free tier on GCP

**When to use Kafka instead:**
- Multi-cloud environments where you need vendor-neutral messaging
- When you need message replay beyond 7 days
- When consumers need very fine-grained offset control

---

## 2. Why Dataflow instead of Spark?

**Decision:** Use Apache Beam on Dataflow for streaming pipeline.

**Alternatives considered:** Apache Spark on Dataproc, Cloud Functions

**Why Dataflow:**
- Unified batch + streaming model (same code, different runner)
- Auto-scaling — spins up workers as message volume increases
- Native Pub/Sub and BigQuery connectors
- Serverless — no cluster management

**Why not Spark:**
- Dataproc requires cluster management and minimum cluster costs
- Spark Streaming has higher latency than Beam
- More complex setup for simple Pub/Sub → BigQuery pipeline

**Why not Cloud Functions:**
- Cloud Functions has 9-minute timeout — unsuitable for streaming
- No windowing or stateful processing support
- Would need separate trigger for each message

---

## 3. Why Cloud Run instead of Cloud Functions (for batch)?

**Decision:** Use Cloud Run Jobs for CSV batch processing.

**Alternatives considered:** Cloud Functions Gen 2, Cloud Composer (Airflow)

**Why Cloud Run Jobs:**
- Up to 24-hour timeout — handles large CSV files
- Full Docker container — any language, any library
- Pay only when running — no idle costs
- Triggered by Eventarc on GCS file upload

**Why not Cloud Functions:**
- Even Gen 2 has 60-minute timeout
- Limited to single-file deployments
- Cannot install system-level dependencies

**Why not Cloud Composer:**
- Minimum cost ~$300/month — too expensive for free tier
- Overkill for simple file-triggered batch jobs
- Airflow is better suited for complex multi-step DAGs

---

## 4. Why BigQuery as the main warehouse?

**Decision:** Use BigQuery with medallion architecture (Bronze/Silver/Gold).

**Alternatives considered:** Cloud Spanner, AlloyDB, Redshift

**Why BigQuery:**
- Serverless — no infrastructure to manage
- Columnar storage — fast analytical queries
- Partitioning + clustering for cost optimization
- Native Dataform integration
- BigQuery ML — train models without leaving the warehouse
- 10GB free storage + 1TB free queries per month

**Medallion Architecture decision:**
raw_layer (Bronze) ← immutable, exactly as received
processed_layer (Silver) ← cleaned, deduplicated, typed
analytics_layer (Gold) ← aggregated, business-ready
ml_layer ← ML models and predictions


Each layer has a specific purpose — raw data is never modified,
ensuring full auditability and the ability to reprocess from scratch.

---

## 5. Why Bigtable for real-time reads?

**Decision:** Use Bigtable for current sensor readings (latest value per sensor).

**Alternatives considered:** Firestore, Cloud Spanner, Redis (Memorystore)

**Why Bigtable:**
- Sub-10ms latency for single-row lookups
- Designed for time-series data (sensor readings)
- Row key design: `zone_id#sensor_id` enables efficient zone-level queries
- HBase-compatible API

**Why not Firestore:**
- Firestore is a document store — better for hierarchical data
- Higher latency than Bigtable for high-throughput reads
- More expensive at scale

**Why not BigQuery for real-time reads:**
- BigQuery has ~2-3 second query latency minimum
- Designed for analytical queries, not point lookups
- Dashboard showing "current AQI" needs <100ms response

**Row key design decision:**
zone_id#sensor_id e.g. zone-01-hitech-city#TRF-001

This allows efficient queries like "give me all sensors in zone 1"
using Bigtable's prefix scan capability.

---

## 6. Why Dataform instead of dbt?

**Decision:** Use Dataform for SQL transformations in BigQuery.

**Alternatives considered:** dbt Core, dbt Cloud, raw SQL scripts

**Why Dataform:**
- Native GCP service — no additional infrastructure
- Built-in BigQuery integration
- `ref()` function for dependency management
- Free for GCP users
- Supports SQLX (SQL + JavaScript config)

**Why not dbt Core:**
- Requires Python environment and orchestration (Airflow/Cloud Scheduler)
- No native GCP managed execution
- More setup complexity

**Why not dbt Cloud:**
- Paid service ($50+/month for team plan)
- Overkill for single-user project

---

## 7. Why BigQuery ML instead of Vertex AI?

**Decision:** Use BigQuery ML for traffic congestion prediction.

**Alternatives considered:** Vertex AI AutoML, scikit-learn on Cloud Run

**Why BigQuery ML:**
- Data never leaves BigQuery — no export/import pipeline
- Train, evaluate, predict all in SQL
- Zero infrastructure — runs on BigQuery's compute
- Free tier included in BigQuery quota
- Perfect for data engineers who know SQL but not Python ML

**Model chosen:** Logistic Regression
- Binary classification: HIGH congestion vs not HIGH
- Interpretable — can explain predictions
- Fast training on 5,000+ rows
- 97.9% accuracy on our dataset

**Why not Vertex AI:**
- Requires Python ML knowledge
- More complex pipeline (training job → endpoint → prediction)
- Costs money for training and serving
- Overkill when BigQuery ML achieves 97.9% accuracy

---

## 8. Why FastAPI instead of Flask?

**Decision:** Use FastAPI for the REST API.

**Alternatives considered:** Flask, Django REST Framework

**Why FastAPI:**
- Automatic Swagger/OpenAPI documentation
- Pydantic models for request/response validation
- Async support for high concurrency
- Python type hints — better developer experience
- 2-3x faster than Flask for I/O bound operations

**Why not Flask:**
- No automatic documentation
- No built-in request validation
- No async support

---

## 9. Why Terraform modules instead of a single main.tf?

**Decision:** Use modular Terraform structure with reusable modules.

**Alternatives considered:** Single main.tf, Pulumi, Google Deployment Manager

**Why Terraform modules:**
- Reusability — same module used for dev and prod
- Separation of concerns — networking module doesn't know about BigQuery
- Testability — each module can be tested independently
- Industry standard — every GCP company uses modular Terraform

**Module structure:**
modules/bigquery/ ← knows how to create BigQuery resources
modules/pubsub/ ← knows how to create Pub/Sub resources
modules/networking/ ← knows how to create VPC resources
envs/dev/ ← calls modules with dev-specific values
envs/prod/ ← calls modules with prod-specific values


---

## 10. Security decisions

**Least privilege IAM:**
- `data-pipeline-sa` — only BigQuery write, Pub/Sub subscribe, GCS read
- `api-sa` — only BigQuery read, Bigtable read, Pub/Sub publish
- `github-actions-sa` — only what CI/CD needs

**No service account keys in code:**
- GitHub Actions uses `GCP_SA_KEY` secret
- Dataform uses Secret Manager for GitHub token
- Application Default Credentials for local development

**Network security:**
- All services run inside `smart-city-vpc`
- Only the API is exposed to the internet
- `deny-all-ingress` firewall rule as default
- Cloud NAT for outbound-only internet access

---

## Data Flow Summary
[IoT Sensors / CSV Files]
↓
[Pub/Sub] ←————————————————— sensor_simulator.py
↓
[Dataflow] ←——— parse → validate → enrich
↓
[BigQuery raw_layer] ←————————— Bronze
↓
[Dataform] ←——— deduplicate → clean → aggregate
↓
[BigQuery processed_layer] ←—— Silver
↓
[BigQuery analytics_layer] ←—— Gold
↓
[BigQuery ML] ←——— train → predict
↓
[ml_layer.traffic_predictions]
↓
[Cloud Run API] ←——— FastAPI serving layer
↓
[Looker Studio] ←—— live dashboard


---

## Performance Optimizations

**BigQuery:**
- All tables partitioned by `DATE(timestamp)` — queries only scan relevant dates
- Clustering by `zone_id` — queries for specific zones scan less data
- This can reduce query costs by 80-90% compared to unpartitioned tables

**Bigtable:**
- Row key design puts `zone_id` first — enables prefix scans
- HDD storage type for development (cheaper, acceptable latency)
- Would use SSD in production for <5ms latency

**API:**
- BigQuery client reused across requests (connection pooling)
- CORS enabled for dashboard integration
- Structured logging for Cloud Monitoring

---

*Last updated: June 2026*
*Author: Jayachandra Reddy*