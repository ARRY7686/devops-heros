# Session 17 Homework: DevSecOps

All topics in `session-17-devsecops/` were done on this machine against the `demo/` Flask app (the "hey-cicd DevSecOps Dashboard"), from a Windows PowerShell terminal, with each security check run locally:

| Pipeline stage (`demo/.github/workflows/devsecops.yml`) | Tool used here |
| :--- | :--- |
| Unit tests | `pytest` + `pytest-cov` |
| SAST (the workflow uses CodeQL, which only runs on GitHub) | **Bandit** 1.9.4 (Python SAST, run locally) |
| SCA | **pip-audit**, plus `trivy fs` |
| Secret scanning | **gitleaks** 8.30.1, plus `trivy fs --scanners secret` |
| Image scan + security gate | **Trivy** 0.75.0 (`--exit-code 1`) |
| Pipeline jobs | **act**: the `test` and `sca` jobs of the real workflow |
| Container registry | Local Docker registry (`registry:2`) on `localhost:5000` instead of Docker Hub/GHCR (no credentials needed) |
| Kubernetes deployment | minikube, namespace `session17` |

Each command and its output is captured in a terminal screenshot under [`screenshots/`](screenshots/), and the plain-text transcript of every step is in [`outputs/`](outputs/).

## Contents

- [Unit tests](#unit-tests)
- [04 SAST](#04-sast)
- [05 SCA](#05-sca)
- [06 Secret scanning](#06-secret-scanning)
- [07 Container image scanning](#07-container-image-scanning)
- [08 Security gates](#08-security-gates)
- [02 Container registry](#02-container-registry)
- [03 Kubernetes deployment](#03-kubernetes-deployment)
- [Findings summary](#findings-summary)
- [Cleanup](#cleanup)

**00-setup/01-tools**

![00-setup/01-tools](screenshots/00-setup/01-tools.png)


## Unit tests

```powershell
pip install -r requirements-dev.txt
pytest --cov=app --cov-report=term-missing
```

**8 passed**, 69% coverage. The tests print `datetime.utcnow()` deprecation warnings, which are worth fixing later.

**01-unit-tests/01-pytest-part1**

![01-unit-tests/01-pytest-part1](screenshots/01-unit-tests/01-pytest-part1.png)

**01-unit-tests/01-pytest-part2**

![01-unit-tests/01-pytest-part2](screenshots/01-unit-tests/01-pytest-part2.png)


## 04 SAST

```powershell
bandit -r app -f screen
```

| Severity | Issue | Where |
| :--- | :--- | :--- |
| **High** | `B201 flask_debug_true`: `app.run(debug=True)` exposes the Werkzeug debugger, which allows arbitrary code execution (CWE-94) | `app/app.py:234` |
| Medium | `B104`: binding to all interfaces (`0.0.0.0`). Expected inside a container | `app/app.py:234` |
| Low ×5 | `B311`: `random` is not cryptographically secure. Acceptable here: the app only uses it to simulate pipeline durations | `app/app.py` |

**Fix.** Turn debug on only when explicitly requested:

```python
app.run(host="0.0.0.0", port=5001, debug=os.environ.get("FLASK_DEBUG") == "1")
```

Re-scanning the fixed copy (`homework/sast-fix/app`) gives **High: 0**.

**04-sast/01-bandit-part1**

![04-sast/01-bandit-part1](screenshots/04-sast/01-bandit-part1.png)

**04-sast/01-bandit-part2**

![04-sast/01-bandit-part2](screenshots/04-sast/01-bandit-part2.png)

**04-sast/02-fix-part1**

![04-sast/02-fix-part1](screenshots/04-sast/02-fix-part1.png)

**04-sast/02-fix-part2**

![04-sast/02-fix-part2](screenshots/04-sast/02-fix-part2.png)


## 05 SCA

| Requirements | pip-audit result |
| :--- | :--- |
| `demo/requirements.txt` (`Flask==3.1.3`) | **No known vulnerabilities found** |
| [`sca-demo/requirements-vulnerable.txt`](sca-demo/requirements-vulnerable.txt) (Flask 2.0.0, Werkzeug 2.0.0, Jinja2 3.0.0, requests 2.19.0, urllib3 1.23) | **71 known vulnerabilities in 6 packages** |
| [`sca-demo/requirements-fixed.txt`](sca-demo/requirements-fixed.txt) (versions from the "Fix Versions" column) | **No known vulnerabilities found** |

Remediation flow: run pip-audit, read the "Fix Versions" column, upgrade the pins, then re-scan until it is clean. My first "fixed" file was not clean: `requests 2.32.5` and `urllib3 2.6.3` still had advisories, and `Werkzeug 3.1.3` had two more. The re-scan caught all of them before they were accepted.

**05-sca/01-pip-audit-app**

![05-sca/01-pip-audit-app](screenshots/05-sca/01-pip-audit-app.png)

**05-sca/03-remediate**

![05-sca/03-remediate](screenshots/05-sca/03-remediate.png)

**05-sca/02-vulnerable-deps-part1**

![05-sca/02-vulnerable-deps-part1](screenshots/05-sca/02-vulnerable-deps-part1.png)

**05-sca/02-vulnerable-deps-part2**

![05-sca/02-vulnerable-deps-part2](screenshots/05-sca/02-vulnerable-deps-part2.png)


## 06 Secret scanning

A demo file with **fake** credentials ([secret-demo/before/config.py](secret-demo/before/config.py)):

```powershell
gitleaks dir before --no-banner -v      # leaks found: 3, exit 1
```

| Rule | Finding |
| :--- | :--- |
| `github-pat` | `ghp_…` token |
| `aws-access-token` | `AKIA…` access key ID |
| `generic-api-key` | AWS secret access key |

**Fix** ([secret-demo/after/config.py](secret-demo/after/config.py)): read each value from the environment (`os.environ.get(...)`). In CI the values come from GitHub Secrets, and in Kubernetes from Secrets. Re-scan: **no leaks found, exit 0**. The `demo/` app itself is also clean, with both gitleaks and `trivy fs --scanners secret`.

If a real secret leaks: revoke and rotate it first, then remove it from Git history. Deleting the file is not enough, because the old commit still contains the secret.

**06-secret-scanning/01-leak**

![06-secret-scanning/01-leak](screenshots/06-secret-scanning/01-leak.png)

**06-secret-scanning/02-fixed**

![06-secret-scanning/02-fixed](screenshots/06-secret-scanning/02-fixed.png)


## 07 Container image scanning

```powershell
docker build -t session17-python:1.0 .
trivy image --severity HIGH,CRITICAL session17-python:1.0
```

Result: **44 HIGH, 0 CRITICAL**. All are in Debian 13 base-image packages (util-linux and similar), mostly with status `affected` and no fixed version yet. The Python packages had none.

**07-image-scanning/01-build**

![07-image-scanning/01-build](screenshots/07-image-scanning/01-build.png)

**07-image-scanning/02-trivy-part1**

![07-image-scanning/02-trivy-part1](screenshots/07-image-scanning/02-trivy-part1.png)

**07-image-scanning/02-trivy-part2**

![07-image-scanning/02-trivy-part2](screenshots/07-image-scanning/02-trivy-part2.png)

**07-image-scanning/02-trivy-part3**

![07-image-scanning/02-trivy-part3](screenshots/07-image-scanning/02-trivy-part3.png)

**07-image-scanning/02-trivy-part4**

![07-image-scanning/02-trivy-part4](screenshots/07-image-scanning/02-trivy-part4.png)

**07-image-scanning/02-trivy-part5**

![07-image-scanning/02-trivy-part5](screenshots/07-image-scanning/02-trivy-part5.png)


## 08 Security gates

```powershell
trivy image --exit-code 1 --severity CRITICAL -q session17-python:1.0
# exit 0 -> GATE PASSED: no critical vulnerabilities - continue to push
```

**The real pipeline under act:**

- `act -l` shows the dependency graph: `test`, `sast` and `sca` run in parallel, then `docker-build` → `image-scan` → `push` → `deploy`.
- `act push -j test`: **8 passed**, job succeeded.
- `act push -j sca`: **job failed, so the gate worked.** The workflow runs a bare `pip-audit`, which audits the *whole runner environment*. It found `pytest 8.4.2 PYSEC-2026-1845` (fixed in 9.0.3), which comes from the runner image, not from `requirements.txt`. Because `docker-build` has `needs: [test, sast, sca]`, nothing would be built or pushed.
  - Fix option 1: audit only the app's dependencies (`pip-audit -r requirements.txt`, which is clean, as shown above).
  - Fix option 2: bump `pytest` in `requirements-dev.txt` to ≥ 9.0.3.

**08-security-gates/01-gate-part1**

![08-security-gates/01-gate-part1](screenshots/08-security-gates/01-gate-part1.png)

**08-security-gates/01-gate-part2**

![08-security-gates/01-gate-part2](screenshots/08-security-gates/01-gate-part2.png)

**08-security-gates/02-pipeline-graph**

![08-security-gates/02-pipeline-graph](screenshots/08-security-gates/02-pipeline-graph.png)

**08-security-gates/03-act-test-job-part1**

![08-security-gates/03-act-test-job-part1](screenshots/08-security-gates/03-act-test-job-part1.png)

**08-security-gates/03-act-test-job-part2**

![08-security-gates/03-act-test-job-part2](screenshots/08-security-gates/03-act-test-job-part2.png)

**08-security-gates/03-act-test-job-part3**

![08-security-gates/03-act-test-job-part3](screenshots/08-security-gates/03-act-test-job-part3.png)

**08-security-gates/03-act-test-job-part4**

![08-security-gates/03-act-test-job-part4](screenshots/08-security-gates/03-act-test-job-part4.png)

**08-security-gates/04-act-sca-job-part1**

![08-security-gates/04-act-sca-job-part1](screenshots/08-security-gates/04-act-sca-job-part1.png)

**08-security-gates/04-act-sca-job-part2**

![08-security-gates/04-act-sca-job-part2](screenshots/08-security-gates/04-act-sca-job-part2.png)

**08-security-gates/04-act-sca-job-part3**

![08-security-gates/04-act-sca-job-part3](screenshots/08-security-gates/04-act-sca-job-part3.png)

**08-security-gates/04-act-sca-job-part4**

![08-security-gates/04-act-sca-job-part4](screenshots/08-security-gates/04-act-sca-job-part4.png)


## 02 Container registry

```powershell
docker run -d -p 5000:5000 --name s17-registry registry:2
docker tag session17-python:1.0 localhost:5000/session17-python:1.0
docker push localhost:5000/session17-python:1.0
Invoke-RestMethod http://localhost:5000/v2/_catalog          # {"repositories":["session17-python"]}
Invoke-RestMethod http://localhost:5000/v2/session17-python/tags/list   # {"tags":["1.0"]}
```

This follows the same flow as GHCR/Docker Hub: build → tag `<registry>/<repo>:<tag>` → push → verify.

**02-container-registry/01-local-registry**

![02-container-registry/01-local-registry](screenshots/02-container-registry/01-local-registry.png)


## 03 Kubernetes deployment

The course `k8s/deployment.yaml` pulls `nensiravaliya28/hey-cicd:__IMAGE_TAG__` from Docker Hub, with the placeholder filled in by CI. Locally, I loaded the scanned image into minikube and used [k8s/deployment.yaml](k8s/deployment.yaml), which uses `image: session17-python:1.0`, `imagePullPolicy: IfNotPresent`, and a `/health` readiness probe. The course `service.yaml` was used unchanged.

- 2/2 Pods `Running`, Service `NodePort 80:30001`.
- Through `kubectl port-forward svc/session17-python 8080:80`:
  - `/health` → `{"status":"healthy",...}`
  - `/api/status` → `{"app":"DevSecOps Dashboard","python_version":"3.12.15",...}`

**03-kubernetes-deployment/01-deploy**

![03-kubernetes-deployment/01-deploy](screenshots/03-kubernetes-deployment/01-deploy.png)

**03-kubernetes-deployment/02-verify**

![03-kubernetes-deployment/02-verify](screenshots/03-kubernetes-deployment/02-verify.png)


## Findings summary

| Check | Finding | Action |
| :--- | :--- | :--- |
| SAST | High: Flask `debug=True` | Gate it behind the `FLASK_DEBUG` env var |
| SCA (app) | Clean | None |
| SCA (pipeline job) | `pytest 8.4.2` CVE in the runner environment fails the gate | Scope pip-audit to `-r requirements.txt` or bump pytest |
| Secrets | Clean (the demo file shows 3 leaks found → fixed) | Use env vars / GitHub Secrets |
| Image | 44 HIGH in Debian base packages, 0 CRITICAL | Gate on CRITICAL; rebuild when Debian ships fixes, or move to a smaller/distroless base |

## Cleanup

Deleted the `session17` namespace, the local registry container, the built images (Docker and minikube), and the pytest cache. The kubectl context was set back to `default`.

**cleanup/01-cleanup**

![cleanup/01-cleanup](screenshots/cleanup/01-cleanup.png)

