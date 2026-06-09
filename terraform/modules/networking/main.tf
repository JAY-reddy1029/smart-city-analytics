# VPC Network
# All our GCP services will run inside this private network
# Nothing is exposed to the internet unless explicitly allowed
resource "google_compute_network" "main" {
  name                    = "smart-city-vpc"
  project                 = var.project_id
  auto_create_subnetworks = false
  description             = "Main VPC for Smart City Analytics Platform"
}

# Subnet for data processing services
# Dataflow, Cloud Run Jobs run here
resource "google_compute_subnetwork" "data_processing" {
  name          = "data-processing-subnet"
  project       = var.project_id
  region        = var.region
  network       = google_compute_network.main.id
  ip_cidr_range = "10.0.1.0/24"

  # Enable private Google access so services can reach
  # GCP APIs without going through the public internet
  private_ip_google_access = true

  description = "Subnet for Dataflow and Cloud Run Jobs"
}

# Subnet for serving layer
# Cloud Run API runs here
resource "google_compute_subnetwork" "serving" {
  name          = "serving-subnet"
  project       = var.project_id
  region        = var.region
  network       = google_compute_network.main.id
  ip_cidr_range = "10.0.2.0/24"

  private_ip_google_access = true

  description = "Subnet for Cloud Run API and serving layer"
}

# Firewall rule: allow internal traffic between subnets
resource "google_compute_firewall" "allow_internal" {
  name    = "allow-internal"
  project = var.project_id
  network = google_compute_network.main.name

  description = "Allow all internal traffic within the VPC"

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  # Only allow traffic from within our VPC subnets
  source_ranges = ["10.0.0.0/8"]
}

# Firewall rule: allow HTTPS traffic to serving layer only
resource "google_compute_firewall" "allow_https_serving" {
  name    = "allow-https-serving"
  project = var.project_id
  network = google_compute_network.main.name

  description = "Allow HTTPS traffic to serving layer"

  allow {
    protocol = "tcp"
    ports    = ["443"]
  }

  # Allow from anywhere (this is the public API)
  source_ranges = ["0.0.0.0/0"]

  # Only applies to resources tagged with this target tag
  target_tags = ["serving-layer"]
}

# Firewall rule: deny all other incoming traffic
resource "google_compute_firewall" "deny_all_ingress" {
  name     = "deny-all-ingress"
  project  = var.project_id
  network  = google_compute_network.main.name
  priority = 65534

  description = "Deny all other ingress traffic"

  deny {
    protocol = "all"
  }

  source_ranges = ["0.0.0.0/0"]
}

# Cloud Router - needed for Cloud NAT
resource "google_compute_router" "main" {
  name    = "smart-city-router"
  project = var.project_id
  region  = var.region
  network = google_compute_network.main.id

  description = "Router for Smart City VPC"
}

# Cloud NAT - allows services in private subnets to reach internet
# (for downloading packages, calling external APIs)
# without exposing them to incoming internet traffic
resource "google_compute_router_nat" "main" {
  name                               = "smart-city-nat"
  project                            = var.project_id
  router                             = google_compute_router.main.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}