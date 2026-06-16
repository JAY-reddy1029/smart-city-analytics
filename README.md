# Smart City Analytics Platform 🏙️

A production-grade, end-to-end data engineering platform built on Google Cloud Platform.
Ingests real-time IoT sensor data from traffic, air quality, and energy monitors across
a smart city — processes, transforms, and serves insights via a REST API and live dashboard.

**Live API:** https://smart-city-api-217338836795.asia-south1.run.app/docs

**Live Dashboard:** https://datastudio.google.com/reporting/d2e16202-4f5f-4736-9008-f8d7d5d84227

---

## 🏗️ Architecture
IoT Sensors / CSV Files / App Events
↓
[ Pub/Sub + Cloud Run ] ← Ingestion Layer
↓
[ Dataflow + Cloud Run Jobs ] ← Processing Layer
↓
[ BigQuery + Bigtable ] ← Storage Layer
↓
[ Dataform + BigQuery ML ] ← Transformation & ML Layer
↓
[ Cloud Run API + Looker Studio] ← Serving Layer
↓
[ Cloud Monitoring + Alerts ] ← Observability Layer


All infrastructure is managed via **Terraform**.
All deployments are automated via **GitHub Actions → Cloud Build**.

---

## 🛠️ Tech Stack

| Layer | Service | Purpose |
|-------|---------|---------|
| Ingestion | Cloud Pub/Sub | Real-time message streaming from IoT sensors |
| Ingestion | Cloud Storage | Raw CSV file landing zone |
| Processing | Dataflow (Apache Beam) | Streaming pipeline: Pub/Sub → BigQuery |
| Processing | Cloud Run Jobs | Batch pipeline: GCS CSV → BigQuery |
| Storage | BigQuery | Main data warehouse (medallion architecture) |
| Storage | Bigtable | Low-latency real-time sensor reads |
| Transformation | Dataform | SQL-based BigQuery transformations |
| ML | BigQuery ML | Traffic prediction model — 97.9% accuracy |
| Serving | Cloud Run | REST API (FastAPI) |
| Serving | Looker Studio | Live dashboards |
| Security | IAM | Least-privilege service accounts |
| Security | Secret Manager | Credentials and API keys |
| Security | VPC + Firewall | Private network, controlled ingress |
| Observability | Cloud Monitoring | Metrics, dashboards, uptime checks |
| Observability | Cloud Logging | Centralised log management |
| IaC | Terraform | All GCP resources as code |
| CI/CD | GitHub Actions | Lint, terraform plan on every push to dev |
| CI/CD | Cloud Build | Build and deploy containers on merge to main |

---

## 📊 Data Domain

**Smart City — 3 sensor types across 10 city zones in Hyderabad:**

| Sensor Type | Metrics | Frequency |
|-------------|---------|-----------|
| Traffic | vehicle_count, avg_speed_kmh, congestion_level | Every 5 seconds |
| Air Quality | co2_ppm, pm25_ugm3, aqi_score, temperature_c | Every 30 seconds |
| Energy | consumption_kwh, voltage_v, power_factor | Every 60 seconds |

**10 zones:** Hitech City, Banjara Hills, Jubilee Hills, Gachibowli, Madhapur,
Kondapur, Kukatpally, Secunderabad, Begumpet, Ameerpet

---

## 🗂️ Project Structure
smart-city-analytics/
├── .github/workflows/ # GitHub Actions CI/CD pipelines
├── definitions/ # Dataform SQL definitions (required at root by Dataform)
│ ├── sources/ # Raw layer source declarations
│ ├── silver/ # Cleaned and validated tables
│ └── gold/ # Aggregated business-ready tables
├── includes/ # Dataform shared constants (required at root by Dataform)
├── terraform/
│ ├── modules/ # Reusable Terraform modules
│ │ ├── bigquery/ # Datasets and tables
│ │ ├── pubsub/ # Topics and subscriptions
│ │ ├── cloudrun/ # Cloud Run services
│ │ ├── bigtable/ # Bigtable instance and tables
│ │ └── networking/ # VPC, subnets, firewall rules
│ └── envs/
│ ├── dev/ # Dev environment config
│ └── prod/ # Prod environment config
├── ingestion/
│ ├── sensor_simulator/ # Python IoT sensor data generator
│ └── gcs_loader/ # Batch CSV file loader
├── processing/
│ ├── dataflow/ # Apache Beam streaming pipeline
│ └── cloud_run_jobs/ # Containerised batch jobs
├── transformation/
│ └── dataform/ # Dataform source files (reference copy)
├── ml/
│ └── bqml/ # BigQuery ML model definitions
├── serving/
│ └── api/ # FastAPI REST API (Cloud Run)
├── monitoring/
│ ├── dashboards/ # Cloud Monitoring dashboard configs
│ └── alerts/ # Alerting policy definitions
├── tests/
│ ├── unit/ # Unit tests
│ └── integration/ # Integration tests
├── docs/ # Architecture docs and decisions
├── scripts/ # Data generation and utility scripts
├── workflow_settings.yaml # Dataform project config (required at root)
└── package.json # Dataform Node.js dependencies (required at root)


> **Note:** `workflow_settings.yaml`, `definitions/`, `includes/`, and `package.json`
> at the repository root are required by Google Dataform — it expects these files at
> the repository root for compilation. The full Dataform source is also maintained
> under `transformation/dataform/` for reference.

---

## 🚀 Getting Started

### Prerequisites
- Google Cloud account with billing enabled
- `gcloud` CLI installed and authenticated
- `terraform` v1.8.0+
- Python 3.11+
- Docker Desktop
- Git

### Setup

**1. Clone the repository**
```bash
git clone https://github.com/JAY-reddy1029/smart-city-analytics.git
cd smart-city-analytics
git checkout dev
```

**2. Authenticate with GCP**
```bash
gcloud auth login
gcloud config set project smart-city-analytics
gcloud auth application-default login
```

**3. Deploy infrastructure**
```bash
cd terraform/envs/dev
terraform init
terraform plan
terraform apply
```

**4. Run the sensor simulator**
```bash
cd ingestion/sensor_simulator
pip install -r requirements.txt
python simulator.py
```

**5. Run the batch CSV loader**
```bash
# Generate sample data and upload to GCS
python scripts/generate_sample_data.py

# Execute Cloud Run Job
gcloud run jobs execute csv-loader-job --region=asia-south1
```

**6. Run Dataform transformations**
- Go to GCP Console → BigQuery → Dataform
- Open `smart-city-dataform` repository → `dev` workspace
- Click **Start execution** → **Execute all actions**

---

## 🌐 Live API

**Base URL:** https://smart-city-api-217338836795.asia-south1.run.app

**Swagger Docs:** https://smart-city-api-217338836795.asia-south1.run.app/docs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/traffic/hourly` | GET | Hourly traffic summary all zones |
| `/traffic/hourly/{zone_id}` | GET | Hourly traffic for specific zone |
| `/traffic/predictions` | GET | ML congestion predictions all zones |
| `/traffic/predictions/{zone_id}` | GET | ML predictions for specific zone |
| `/airquality/daily` | GET | Daily air quality all zones |
| `/airquality/daily/{zone_id}` | GET | Daily air quality for specific zone |
| `/energy/daily` | GET | Daily energy consumption all zones  |
| `/energy/daily/{zone_id}` | GET | Daily energy for specific zone |

---

## 🤖 BigQuery ML Model

**Model:** Logistic Regression — Traffic Congestion Prediction

**Predicts:** Will a zone have HIGH congestion at a given hour?

| Metric | Score |
|--------|-------|
| Accuracy | 97.9% |
| Precision | 94.88% |
| Recall | 100% |
| ROC AUC | 1.0 |
| F1 Score | 97.37% |

**Features used:** zone_id, hour_of_day, day_of_week, is_peak_hour,
avg_vehicle_count, avg_speed_kmh, avg_congestion_score

**Training data:** 15,300 rows across 10 zones, 30 days, 17 hours/day

---

## 🔄 CI/CD Pipeline
Developer pushes to dev branch
↓
GitHub Actions triggered automatically
↓
├── Code Quality (Black + Flake8) ✅
└── Terraform Plan (dry run) ✅
↓
Developer raises Pull Request: dev → main
↓
PR reviewed and merged
↓
GitHub Actions triggered automatically
↓
├── Terraform Apply (infrastructure deployed)
├── Build + Push Docker images to Artifact Registry
├── Deploy API to Cloud Run
└── Update CSV Loader Cloud Run Job
↓
Live on GCP ✅


**GitHub Actions Workflows:** `.github/workflows/ci-cd.yml`
- 5 jobs: Code Quality, Terraform Plan, Terraform Apply, Deploy API, Deploy CSV Loader
- Runs in ~37 seconds on every push

---

## 📐 Architecture Decisions

See [docs/architecture.md](docs/architecture.md) for detailed explanations of every
service choice — why Bigtable over Firestore, why Cloud Run over Cloud Functions,
why Dataflow over Spark, why BigQuery ML over Vertex AI, and more.

---

## 📈 Project Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Foundation — GCP setup, Terraform base | ✅ Complete |
| 2 | Ingestion — Pub/Sub + sensor simulator | ✅ Complete |
| 3 | Streaming pipeline — Dataflow (Apache Beam) | ✅ Complete |
| 4 | Batch pipeline — Cloud Run Jobs | ✅ Complete |
| 5 | Storage — BigQuery + Bigtable | ✅ Complete |
| 6 | Transformation — Dataform (Bronze→Silver→Gold) | ✅ Complete |
| 7 | ML — BigQuery ML traffic prediction (97.9% accuracy) | ✅ Complete |
| 8 | Serving — Cloud Run API (FastAPI, 9 endpoints) | ✅ Complete |
| 9 | Dashboard — Looker Studio (2 pages, live) | ✅ Complete |
| 10 | Security — IAM + Secret Manager + VPC | ✅ Complete |
| 11 | Monitoring — Cloud Monitoring + Alerts | ⏳ Pending |
| 12 | CI/CD — GitHub Actions (5 jobs, runs in 37s) | ✅ Complete |

---

## 👤 Author

**Jayachandra Reddy**
- Location: Hyderabad, India
- GitHub: [@JAY-reddy1029](https://github.com/JAY-reddy1029)
- Email: p.v.jay2003@gmail.com

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.