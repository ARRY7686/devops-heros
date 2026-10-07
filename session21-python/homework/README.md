# Session 21 Homework: DevOps Final Capstone (TaskBoard)

The TaskBoard capstone in `session21-python/` is a React frontend, a FastAPI backend and PostgreSQL. It was taken through every module of `GRADING.md` on this machine, from a Windows PowerShell terminal.

| Module | Done with |
| :--- | :--- |
| M1 App + M4 Docker | `docker compose` (backend, frontend, postgres) |
| M2 Testing | `pytest` in a `python:3.12-slim` container (the backend pins need Python 3.12) |
| M3 Git | repo history, `.gitignore`, gitleaks |
| M5 CI/CD | the real `.github/workflows/ci-cd.yml` run locally with **act** |
| M6 DevSecOps | **Trivy** image and config scans |
| M7 Terraform | VPC + EKS modules applied to the **Moto** AWS emulator (no AWS credentials on this machine, and a real EKS cluster plus NAT gateway costs money) |
| M8 Kubernetes + Helm | minikube, Helm chart, ingress-nginx addon, HPA |
| M9 Observability | `kube-prometheus-stack` (Prometheus Operator + Grafana) with the chart's `ServiceMonitor` |
| Troubleshooting lab | broken image + broken Service |

Several real bugs in the capstone code turned up along the way. Each is diagnosed and fixed in a copy under `homework/`; the course files were not modified. They are listed in [Bugs found and fixed](#bugs-found-and-fixed).

Each command and its output is captured in a terminal screenshot under [`screenshots/`](screenshots/), and the plain-text transcript of every step is in [`outputs/`](outputs/).

## Contents

- [Bugs found and fixed](#bugs-found-and-fixed)
- [M1 + M4: Application and Docker](#m1--m4-application-and-docker)
- [M2: Testing](#m2-testing)
- [M3: Git](#m3-git)
- [M5: CI/CD](#m5-cicd)
- [M6: Trivy](#m6-trivy)
- [M7: Terraform](#m7-terraform)
- [M8: Kubernetes + Helm](#m8-kubernetes--helm)
- [M9: Prometheus + Grafana](#m9-prometheus--grafana)
- [Troubleshooting lab](#troubleshooting-lab)
- [Cleanup](#cleanup)

## Bugs found and fixed

| # | Where | Symptom | Root cause | Fix |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `docker-compose.yml` | `backend` **Exited (1)** a second after `docker compose up` | `depends_on: [postgres]` only waits for the container to *start*. `alembic upgrade head` then gets `connection refused` and the process exits | [compose/docker-compose.healthcheck.yml](compose/docker-compose.healthcheck.yml): a `pg_isready` healthcheck, `condition: service_healthy`, and `restart: on-failure` |
| 2 | `backend/tests/test_api.py` | `test_create_task_validation` **FAILED**: `sqlite3.OperationalError: no such table: tasks`. The act CI `test` job fails with it | A module-level `TestClient(app)` never runs FastAPI's startup event (`Base.metadata.create_all`) | [tests-fixed/test_api.py](tests-fixed/test_api.py): `with TestClient(app) as c` fixture. Also extended from 3 to **8 tests** covering 6 endpoints (rubric: ≥5 tests, ≥3 endpoints) |
| 3 | `terraform/*.tf` | `terraform init`: **Invalid single-argument block definition** | Every block is written on one line with several arguments, which HCL does not allow | [terraform-fixed/](terraform-fixed/): the same configuration formatted as multi-line HCL |
| 4 | `helm/.../ingress.yaml` | `/api` through the Ingress returns **HTTP 503**. `describe ingress`: `taskboard-backend:8080 (<error: services "taskboard-backend" not found>)` | The backend Service is named `<release>-taskboard-backend` and listens on **8000** | [helm/taskboard/templates/ingress.yaml](helm/taskboard/templates/ingress.yaml) uses `{{ include "taskboard.fullname" . }}-backend` on port 8000 |
| 5 | frontend on Kubernetes | `taskboard-frontend` **CrashLoopBackOff**: `nginx: [emerg] host not found in upstream "backend"` | The image's `nginx.conf` proxies `/api/` to `http://backend:8000` (the Compose service name). There is no Service called `backend` in Kubernetes | [helm/taskboard/templates/backend-alias-service.yaml](helm/taskboard/templates/backend-alias-service.yaml) adds a Service named `backend` → backend Pods |
| 6 | `troubleshooting/broken-service.yaml` | README §24 references it, but the file is missing from the repo | — | Recreated it in [troubleshooting/](troubleshooting/) |

Other findings, not fixed:
- The frontend container runs as **root** (`uid=0`); the rubric expects a non-root user in both Dockerfiles.
- `on_event` is deprecated in FastAPI; use lifespan handlers.
- Trivy config checks flag the chart's Deployments for having no `securityContext` / `readOnlyRootFilesystem`.

## M1 + M4: Application and Docker

```powershell
docker compose up --build -d            # backend Exited (1): bug 1
docker compose logs backend             # psycopg.OperationalError: connection ... failed
docker compose -f docker-compose.yml -f homework\compose\docker-compose.healthcheck.yml up -d
```

With the healthcheck, Compose waits for `postgres (healthy)` before starting the backend: `Application startup complete`.

**API (all CRUD endpoints):**
- `GET /health` → `{"status":"UP"}`, `GET /ready` → `{"status":"READY"}`.
- `POST /api/tasks` ×2, then `GET /api/tasks`, `PUT` (status → DONE), `GET /api/tasks/stats` → `{"total":2,"todo":1,"inProgress":0,"done":1}`.
- `DELETE` → **204**.

**Frontend:** `http://localhost:3000` serves the React app (`<title>TaskBoard</title>`), and `/api/tasks` through its nginx proxy returns the same data.

**Database:** `alembic current` shows `0001_create_tasks (head)`, and `psql \dt` lists the `alembic_version` and `tasks` tables.

**Metrics:** `/metrics` exposes `http_requests_total{handler,method,status}` for every endpoint.

**Dockerfiles:** the backend is `python:3.12-slim` running as `uid=10001(appuser)`. The frontend is a multi-stage `node:22-alpine` → `nginx:1.27-alpine` build, running as root (finding above).

**m1-m4-docker-compose/02-api-crud**

![m1-m4-docker-compose/02-api-crud](screenshots/m1-m4-docker-compose/02-api-crud.png)

**m1-m4-docker-compose/03-frontend-db-metrics**

![m1-m4-docker-compose/03-frontend-db-metrics](screenshots/m1-m4-docker-compose/03-frontend-db-metrics.png)

**m1-m4-docker-compose/04-dockerfiles**

![m1-m4-docker-compose/04-dockerfiles](screenshots/m1-m4-docker-compose/04-dockerfiles.png)

**m1-m4-docker-compose/05-down**

![m1-m4-docker-compose/05-down](screenshots/m1-m4-docker-compose/05-down.png)

**m1-m4-docker-compose/01-up-part1**

![m1-m4-docker-compose/01-up-part1](screenshots/m1-m4-docker-compose/01-up-part1.png)

**m1-m4-docker-compose/01-up-part2**

![m1-m4-docker-compose/01-up-part2](screenshots/m1-m4-docker-compose/01-up-part2.png)

**m1-m4-docker-compose/01b-healthcheck-fix**

![m1-m4-docker-compose/01b-healthcheck-fix](screenshots/m1-m4-docker-compose/01b-healthcheck-fix.png)


## M2: Testing

| Test suite | Result |
| :--- | :--- |
| Original `backend/tests/test_api.py` (3 tests) | 2 passed, **1 failed** (`no such table: tasks`, bug 2) |
| Fixed `homework/tests-fixed/test_api.py` (8 tests) | **8 passed** |

The 8 tests are: health, root, create, validation (empty title → 422), list+get, update status, delete then 404, and stats. They use SQLite (`sqlite:///./test.db`), not the production database. `pytest.ini` sets `pythonpath = .`.

**m2-testing/01-pytest-part1**

![m2-testing/01-pytest-part1](screenshots/m2-testing/01-pytest-part1.png)

**m2-testing/01-pytest-part2**

![m2-testing/01-pytest-part2](screenshots/m2-testing/01-pytest-part2.png)

**m2-testing/01-pytest-part3**

![m2-testing/01-pytest-part3](screenshots/m2-testing/01-pytest-part3.png)

**m2-testing/01-pytest-part4**

![m2-testing/01-pytest-part4](screenshots/m2-testing/01-pytest-part4.png)

**m2-testing/01-pytest-part5**

![m2-testing/01-pytest-part5](screenshots/m2-testing/01-pytest-part5.png)

**m2-testing/01-pytest-part6**

![m2-testing/01-pytest-part6](screenshots/m2-testing/01-pytest-part6.png)

**m2-testing/01-pytest-part7**

![m2-testing/01-pytest-part7](screenshots/m2-testing/01-pytest-part7.png)

**m2-testing/02-pytest-fixed**

![m2-testing/02-pytest-fixed](screenshots/m2-testing/02-pytest-fixed.png)


## M3: Git

`git log` shows the capstone commit (`d07887f session21 python added`). There are 62 tracked files, and `.gitignore` excludes `.idea/`, `.vscode/`, `node_modules/`, `dist/`, `*.log`, `.env`, `.terraform/` and `*.tfstate*`. `gitleaks dir .` reports **no leaks found**.

**m3-git/01-repo**

![m3-git/01-repo](screenshots/m3-git/01-repo.png)


## M5: CI/CD

`act -l` shows three stages: **test → build-scan-push → deploy**.

`act push -j test` ran the real test job: setup-python 3.12, `pip install`, `pytest -q`, setup-node 22, then the frontend build. It **failed with `1 failed, 2 passed`**, the same test bug. This is the pipeline doing its job and stopping the build. `build-scan-push` needs GHCR credentials and `deploy` needs a real cluster kubeconfig, so those two jobs were not run locally. Their work (image build, Trivy scan, Helm deploy) is shown in M4, M6 and M8.

**m5-cicd/01-pipeline**

![m5-cicd/01-pipeline](screenshots/m5-cicd/01-pipeline.png)

**m5-cicd/02-test-job-part1**

![m5-cicd/02-test-job-part1](screenshots/m5-cicd/02-test-job-part1.png)

**m5-cicd/02-test-job-part2**

![m5-cicd/02-test-job-part2](screenshots/m5-cicd/02-test-job-part2.png)

**m5-cicd/02-test-job-part3**

![m5-cicd/02-test-job-part3](screenshots/m5-cicd/02-test-job-part3.png)

**m5-cicd/02-test-job-part4**

![m5-cicd/02-test-job-part4](screenshots/m5-cicd/02-test-job-part4.png)

**m5-cicd/02-test-job-part5**

![m5-cicd/02-test-job-part5](screenshots/m5-cicd/02-test-job-part5.png)

**m5-cicd/02-test-job-part6**

![m5-cicd/02-test-job-part6](screenshots/m5-cicd/02-test-job-part6.png)

**m5-cicd/02-test-job-part7**

![m5-cicd/02-test-job-part7](screenshots/m5-cicd/02-test-job-part7.png)

**m5-cicd/02-test-job-part8**

![m5-cicd/02-test-job-part8](screenshots/m5-cicd/02-test-job-part8.png)

**m5-cicd/02-test-job-part9**

![m5-cicd/02-test-job-part9](screenshots/m5-cicd/02-test-job-part9.png)

**m5-cicd/02-test-job-part10**

![m5-cicd/02-test-job-part10](screenshots/m5-cicd/02-test-job-part10.png)


## M6: Trivy

| Target | HIGH | CRITICAL |
| :--- | :--- | :--- |
| `taskboard-backend:local`, Debian 13 OS packages | 44 | 0 |
| `taskboard-backend:local`, Python packages | 3 | 0 |
| `taskboard-frontend:local` (alpine 3.21.3) | 42 | **2** |
| `trivy config helm/taskboard` | 3 per Deployment (no securityContext, writable root FS) | 0 |
| `trivy config backend/Dockerfile` / `frontend/Dockerfile` | — | — |

A `--severity CRITICAL --exit-code 1` gate (as in Session 17) would **block the frontend image**. The fix is to rebuild it on a newer `nginx:alpine` base.

**m6-trivy/01-images-part1**

![m6-trivy/01-images-part1](screenshots/m6-trivy/01-images-part1.png)

**m6-trivy/01-images-part2**

![m6-trivy/01-images-part2](screenshots/m6-trivy/01-images-part2.png)

**m6-trivy/01-images-part3**

![m6-trivy/01-images-part3](screenshots/m6-trivy/01-images-part3.png)

**m6-trivy/01-images-part4**

![m6-trivy/01-images-part4](screenshots/m6-trivy/01-images-part4.png)

**m6-trivy/01-images-part5**

![m6-trivy/01-images-part5](screenshots/m6-trivy/01-images-part5.png)

**m6-trivy/01-images-part6**

![m6-trivy/01-images-part6](screenshots/m6-trivy/01-images-part6.png)

**m6-trivy/02-frontend-part1**

![m6-trivy/02-frontend-part1](screenshots/m6-trivy/02-frontend-part1.png)

**m6-trivy/02-frontend-part2**

![m6-trivy/02-frontend-part2](screenshots/m6-trivy/02-frontend-part2.png)

**m6-trivy/02-frontend-part3**

![m6-trivy/02-frontend-part3](screenshots/m6-trivy/02-frontend-part3.png)

**m6-trivy/02-frontend-part4**

![m6-trivy/02-frontend-part4](screenshots/m6-trivy/02-frontend-part4.png)

**m6-trivy/03-config-part1**

![m6-trivy/03-config-part1](screenshots/m6-trivy/03-config-part1.png)

**m6-trivy/03-config-part2**

![m6-trivy/03-config-part2](screenshots/m6-trivy/03-config-part2.png)

**m6-trivy/03-config-part3**

![m6-trivy/03-config-part3](screenshots/m6-trivy/03-config-part3.png)

**m6-trivy/03-config-part4**

![m6-trivy/03-config-part4](screenshots/m6-trivy/03-config-part4.png)

**m6-trivy/03-config-part5**

![m6-trivy/03-config-part5](screenshots/m6-trivy/03-config-part5.png)

**m6-trivy/03-config-part6**

![m6-trivy/03-config-part6](screenshots/m6-trivy/03-config-part6.png)


## M7: Terraform

1. The original `terraform/` fails at `terraform init` with **Invalid single-argument block definition** (bug 3).
2. With [terraform-fixed/](terraform-fixed/), against the Moto emulator (`MOTO_IAM_LOAD_MANAGED_POLICIES=true` so the AWS-managed EKS policies exist):
   - `terraform init` downloads the `terraform-aws-modules/vpc` 5.8.1 and `eks` 20.37.1 modules, and `fmt -check` and `validate` pass.
   - `terraform plan`: **Plan: 54 to add**.
   - `terraform apply`: **51 resources created**, including the VPC, 2 public and 2 private subnets, a NAT gateway, IAM roles, a KMS key, the EKS cluster `taskboard-eks` and the managed node group `main`.
     - `aws eks describe-cluster` → **ACTIVE, version 1.31**. `list-nodegroups` shows the node group.
     - The 3 resources that did not apply are the EKS **access-entry** resources (`enable_cluster_creator_admin_permissions`), because Moto does not implement the `CreateAccessEntry` API. On real AWS they would be created.
   - `terraform destroy`: **51 destroyed**, and `state list` is empty.

**m7-terraform/01-original-config-error**

![m7-terraform/01-original-config-error](screenshots/m7-terraform/01-original-config-error.png)

**m7-terraform/02-fixed-init-validate-part1**

![m7-terraform/02-fixed-init-validate-part1](screenshots/m7-terraform/02-fixed-init-validate-part1.png)

**m7-terraform/02-fixed-init-validate-part2**

![m7-terraform/02-fixed-init-validate-part2](screenshots/m7-terraform/02-fixed-init-validate-part2.png)

**m7-terraform/03-plan-part1**

![m7-terraform/03-plan-part1](screenshots/m7-terraform/03-plan-part1.png)

**m7-terraform/03-plan-part2**

![m7-terraform/03-plan-part2](screenshots/m7-terraform/03-plan-part2.png)

**m7-terraform/04-apply**

![m7-terraform/04-apply](screenshots/m7-terraform/04-apply.png)

**m7-terraform/05-verify-part1**

![m7-terraform/05-verify-part1](screenshots/m7-terraform/05-verify-part1.png)

**m7-terraform/05-verify-part2**

![m7-terraform/05-verify-part2](screenshots/m7-terraform/05-verify-part2.png)

**m7-terraform/06-destroy**

![m7-terraform/06-destroy](screenshots/m7-terraform/06-destroy.png)


## M8: Kubernetes + Helm

1. `minikube addons enable ingress` installs the ingress-nginx controller.
2. The images built by Compose were tagged `taskboard-backend:local` / `taskboard-frontend:local` and loaded into minikube. [helm/values-local.yaml](helm/values-local.yaml) points the chart at them instead of `ghcr.io/YOUR_ORG/...`.
3. **Original chart** (`helm upgrade --install taskboard ./helm/taskboard -f values-local.yaml -f values-dev.yaml`):
   - The frontend goes into **CrashLoopBackOff** (bug 5).
   - `/api` through the Ingress returns **503** (bug 4).
   - The backend restarts a few times until Postgres is ready, the same race as bug 1; the readiness/liveness probes recover it.
4. **Fixed chart** (`helm upgrade taskboard homework/helm/taskboard ...` = revision 2, then `rollout restart deployment/taskboard-frontend`):
   - All Pods are Running.
   - The Ingress backends are `taskboard-taskboard-backend:8000 (10.244.x.x:8000)` and `taskboard-frontend:80`.
   - Through the Ingress (`Host: taskboard.local`): `/api/tasks` → **HTTP 200**, `POST /api/tasks` creates "Deployed on Kubernetes via Helm", and `/` → **HTTP 200** with the TaskBoard UI.
5. **HPA** (`--set hpa.enabled=true`, minReplicas 2, maxReplicas 6, target 60% CPU): three busybox load pods hammered `/api/tasks`. `kubectl get hpa` showed `cpu: 262%/60%`, and the backend Deployment scaled **2 → 6/6 replicas**. `helm list` / `helm history` show the release revisions.

Note: the first full run (HPA, monitoring) used the chart with `serviceMonitor.enabled=true` (the default). The bug re-run in steps 03–07 used `--set monitoring.serviceMonitor.enabled=false`, because the monitoring stack (and its ServiceMonitor CRD) had already been removed by then.

**m8-kubernetes/01-ingress-controller**

![m8-kubernetes/01-ingress-controller](screenshots/m8-kubernetes/01-ingress-controller.png)

**m8-kubernetes/02-load-images**

![m8-kubernetes/02-load-images](screenshots/m8-kubernetes/02-load-images.png)

**m8-kubernetes/03-helm-install-original**

![m8-kubernetes/03-helm-install-original](screenshots/m8-kubernetes/03-helm-install-original.png)

**m8-kubernetes/04-troubleshoot-frontend**

![m8-kubernetes/04-troubleshoot-frontend](screenshots/m8-kubernetes/04-troubleshoot-frontend.png)

**m8-kubernetes/05-troubleshoot-ingress**

![m8-kubernetes/05-troubleshoot-ingress](screenshots/m8-kubernetes/05-troubleshoot-ingress.png)

**m8-kubernetes/06-fix-chart-part1**

![m8-kubernetes/06-fix-chart-part1](screenshots/m8-kubernetes/06-fix-chart-part1.png)

**m8-kubernetes/06-fix-chart-part2**

![m8-kubernetes/06-fix-chart-part2](screenshots/m8-kubernetes/06-fix-chart-part2.png)

**m8-kubernetes/07-ingress-works**

![m8-kubernetes/07-ingress-works](screenshots/m8-kubernetes/07-ingress-works.png)

**m8-kubernetes/08-hpa**

![m8-kubernetes/08-hpa](screenshots/m8-kubernetes/08-hpa.png)


## M9: Prometheus + Grafana

- `helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring -f monitoring/prometheus-values.yaml` installs Prometheus, Alertmanager, Grafana, node-exporter, kube-state-metrics and the operator.
- The chart's **ServiceMonitor** `taskboard-taskboard-backend` was picked up. Prometheus targets show all **6 backend pods `up`** at `http://<pod-ip>:8000/metrics`.
- PromQL `sum by (handler) (http_requests_total{namespace="taskboard"})` gives `/api/tasks` **92,283** requests (the HPA load test), plus `/ready`, `/health`, `/metrics` and `/api/tasks/stats`.
- Grafana: `/api/health` OK. The admin password comes from the `kube-prometheus-stack-grafana` Secret. The bundled dashboards are listed (Kubernetes / Compute Resources, CoreDNS, etcd, and more). The data-source list came back empty through the API because kube-prometheus-stack provisions its Prometheus data source from a sidecar ConfigMap; the dashboards that use it are present.

**m9-monitoring/01-kube-prometheus-stack**

![m9-monitoring/01-kube-prometheus-stack](screenshots/m9-monitoring/01-kube-prometheus-stack.png)

**m9-monitoring/02-prometheus**

![m9-monitoring/02-prometheus](screenshots/m9-monitoring/02-prometheus.png)

**m9-monitoring/03-grafana**

![m9-monitoring/03-grafana](screenshots/m9-monitoring/03-grafana.png)


## Troubleshooting lab

| Lab | Observed | Root cause | Fix |
| :--- | :--- | :--- | :--- |
| `troubleshooting/broken-image.yaml` | `ErrImagePull` → `ImagePullBackOff` | `ghcr.io/example/taskboard-backend:does-not-exist`: tag missing / registry denies the pull (403 on the token request) | Use a valid, pullable image; deleted the Deployment |
| `broken-service.yaml` (recreated) | `taskboard-broken-service` endpoints: `<none>` | Selector `app=taskboard-api`, but the Pods are labelled `app=taskboard-backend` (`get pods --show-labels`) | [fixed-service.yaml](troubleshooting/fixed-service.yaml): endpoints list the backend pod IPs |

**troubleshooting/01-broken-image**

![troubleshooting/01-broken-image](screenshots/troubleshooting/01-broken-image.png)

**troubleshooting/02-broken-service**

![troubleshooting/02-broken-service](screenshots/troubleshooting/02-broken-service.png)


## Cleanup

- Uninstalled both Helm releases (`taskboard`, `kube-prometheus-stack`).
- Deleted the `monitoring.coreos.com` CRDs and the `taskboard` and `monitoring` namespaces.
- Disabled the ingress addon, which was disabled before.
- Removed the `prometheus-community` Helm repo, the images (Docker and minikube) and the Moto container.
- Ran `docker compose down -v`.
- Deleted the Terraform working files and `backend/test.db`.

`git status` shows only the new `homework/` folder.

**cleanup/01-cleanup**

![cleanup/01-cleanup](screenshots/cleanup/01-cleanup.png)

