# TicketForge — On-Prem DevOps → Lift & Shift to AWS Cloud

A production-grade, event-driven microservices platform simulating a high-traffic ticketing system. Built to demonstrate the full DevOps lifecycle: **local development → on-prem VM deployment (Vagrant) → cloud lift & shift (AWS + Terraform + EKS + ArgoCD)**.

## Architecture

```
Client → API Gateway (port 8000) → Ticket Service (port 8081) → Kafka → Payment Service (port 8082) → Kafka → Notification Service (port 8083)
```

| Service | Stack | Role |
|---|---|---|
| **API Gateway** | Java 21 / Spring Cloud Gateway | Rate limiting (Redis token buckets, 10 req/s, burst 20), request routing |
| **Ticket Service** | Java 21 / Spring Boot + JPA | Redis distributed locks (`SETNX`), PostgreSQL persistence, Kafka producer |
| **Payment Service** | Python 3.11 / FastAPI + AIOKafka | Kafka consumer, mock payment (every 7th fails), emits confirm/fail events |
| **Notification Service** | Python 3.11 / FastAPI + AIOKafka + FPDF2 | Consumes confirmations, generates PDF tickets, simulates email delivery |

## The DevOps Journey

This project documents two infrastructure paths:

1. **On-Prem DevOps** — Vagrant-managed VM running the full stack via Docker Compose
2. **Lift & Shift to AWS Cloud** — Terraform-provisioned EKS cluster with ArgoCD GitOps

---

## Part 1: On-Prem DevOps (Vagrant)

A single `Vagrantfile` provisions an Ubuntu VM, installs Docker, builds all service images, and runs the full stack — simulating an on-premise data centre deployment.

### Prerequisites

- [Vagrant](https://www.vagrantup.com/downloads) + [VirtualBox](https://www.virtualbox.org/)
- At least 4 GB RAM available for the VM

### Quick Start

```bash
vagrant up
```

This will:
1. Provision an Ubuntu 22.04 VM (4 GB RAM, 2 CPUs)
2. Install Docker + Docker Compose
3. Build all 4 service images
4. Start PostgreSQL, Redis, Kafka, and all services

The services are exposed on your host:
| Service | Host Port | VM Port |
|---|---|---|
| API Gateway | `8000` | `8000` |
| Ticket Service | `8081` | `8081` |
| Payment Service | `8082` | `8082` |
| Notification Service | `8083` | `8083` |
| Kafka UI | `8084` | `8080` |

### Redeploy After Code Changes

```bash
vagrant provision
```

Or destroy and recreate:

```bash
vagrant destroy -f && vagrant up
```

### Test a Reservation

```bash
curl -X POST "http://localhost:8000/api/v1/tickets/reserve?userId=user42&matchId=MATCH_001&seatNumber=A-15"
```

### CI/CD Pipeline (On-Prem)

The GitHub Actions CI pipelines build, lint, scan (Trivy), and push Docker images to Docker Hub:

| Pipeline | Trigger | Registry |
|---|---|---|
| `ticket-service-ci.yml` | Push to `main` (ticket-service/**) | Docker Hub |
| `api-gateway-ci.yml` | Push to `main` (apigateway/**) | Docker Hub |
| `payment-service-ci.yml` | Push/PR to `master` (payment-service/**) | Docker Hub |
| `notification-service-ci.yml` | Push/PR to `master` (notification-service/**) | Docker Hub |

CD flow: `git push` → CI builds + pushes image → `vagrant provision` pulls new images and restarts services.

### Local Development (Without Vagrant)

```bash
# 1. Start infrastructure
docker compose up -d

# 2. Build & run ticket-service (requires Java 21 + Maven)
cd ticket-service && mvn clean package -DskipTests
java -jar target/ticket-service-0.0.1-SNAPSHOT.jar

# 3. Build & run api-gateway
cd apigateway && mvn clean package -DskipTests
java -jar target/api-gateway-0.0.1-SNAPSHOT.jar

# 4. Run payment-service (requires Python 3.11)
cd payment-service && pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8082

# 5. Run notification-service
cd notification-service && pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8083
```

---

## Part 2: Lift & Shift to AWS Cloud

The same architecture deployed to AWS using Infrastructure as Code (Terraform) and GitOps (ArgoCD). This represents the cloud migration path from the on-prem Vagrant setup.

### Infrastructure (Terraform)

```
terraform/
├── provider.tf    # AWS provider, eu-west-1, default tags
├── vpc.tf         # VPC 10.0.0.0/16, 2 AZs, public/private/database subnets
├── eks.tf         # EKS cluster 1.28, managed node groups (t3.medium, 1-5 nodes)
├── rds.tf         # PostgreSQL 15.4, db.t3.micro, auto-scale to 100 GB
└── ecr.tf         # 4 ECR repositories, KMS encryption, scan-on-push
```

```bash
cd terraform
terraform init && terraform plan
terraform apply -var="db_password=YOUR_SECURE_PASSWORD"
```

### Kubernetes (ArgoCD GitOps)

All services run in EKS under the `future-eagle-prod` namespace, synchronised from the `k8s/` directory via ArgoCD.

```yaml
# k8s/argocd-app.yaml  (auto-sync, prune, self-heal)
```

| Manifest | Replicas | Probe | Type |
|---|---|---|---|
| `ticket-service.yaml` | 2 | readiness (8081/actuator/health) | ClusterIP |
| `api-gateway.yaml` | 2 | readiness (8000/actuator/health) | ClusterIP |
| `payment-service.yaml` | 2 | — | ClusterIP |
| `notification-service.yaml` | 2 | — | ClusterIP |

### Cloud CI/CD Pipeline

The on-prem CI pushes to Docker Hub; the cloud CI pushes to Amazon ECR via GitHub OIDC (passwordless):

```
Push → Checkout → Build → OIDC Auth → ECR Login → Docker Build → Trivy Scan → Push to ECR
```

ArgoCD detects the new image and auto-syncs the cluster.

### Observability

Prometheus scrapes all services + Grafana dashboards, deployed alongside in the cluster (`k8s/prometheus.yaml`, `k8s/grafana.yaml`).

---

## DevSecOps Practices

| Layer | Practice |
|---|---|
| **Containers** | Multi-stage builds, non-root users |
| **CI/CD** | Trivy vulnerability scanning (block on CRITICAL/HIGH), Flake8 lint |
| **Auth** | GitHub OIDC → AWS IAM (cloud path), no long-lived secrets |
| **Registry** | Docker Hub (on-prem), ECR + KMS encryption (cloud) |
| **Network** | VPC subnet isolation, RDS accessible only from EKS SG |

## Project Structure

```
ticket-forge-devops/
├── Vagrantfile              # On-prem VM deployment
├── docker-compose.yml        # Local infrastructure (PostgreSQL, Redis, Kafka)
├── docker-compose.prod.yml   # Full stack (infra + all services)
├── .github/workflows/        # CI pipelines (4 services → Docker Hub)
├── apigateway/               # Java 21 / Spring Cloud Gateway
├── ticket-service/           # Java 21 / Spring Boot + JPA + Kafka
├── payment-service/          # Python 3.11 / FastAPI + AIOKafka
├── notification-service/     # Python 3.11 / FastAPI + AIOKafka + FPDF2
├── terraform/                # AWS IaC (VPC, EKS, RDS, ECR) — Lift & Shift
├── k8s/                      # Kubernetes manifests for EKS
├── automation/               # Ansible playbook, health check & pipeline monitor scripts
├── load-tests/               # k6 spike test (800 concurrent users)
└── docs/                     # Architecture diagrams
```

## Roadmap

- [x] On-prem DevOps (Vagrant)
- [x] CI/CD (GitHub Actions + Docker Hub)
- [ ] Saga pattern for distributed transaction rollback
- [ ] Helm charts for templated K8s deployments
- [ ] k6 / Gatling flash-sale load testing
- [ ] OpenTelemetry + Jaeger distributed tracing
- [ ] Dead letter queue handling for failed events
- [ ] AWS ElastiCache + Amazon MSK (managed cloud services)
