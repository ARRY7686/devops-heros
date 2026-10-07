# Session 16 Homework: CI/CD and GitHub Actions

Every exercise in `session-16-github-actions/` (folders 01 to 09) was run on this machine from a Windows PowerShell terminal.

**How the workflows were run.** Nothing was pushed to GitHub. Each workflow YAML was executed locally with [**act**](https://github.com/nektos/act) (v0.2.89), which runs GitHub Actions jobs in Docker containers using the `catthehacker/ubuntu:act-latest` runner image. act runs the real steps: `actions/checkout`, `actions/setup-python`, `pip`, `pytest`, `flake8`, `actions/upload-artifact` and `download-artifact`, with secrets passed through `-s`. The act config used is:

```text
-P ubuntu-latest=catthehacker/ubuntu:act-latest
--pull=false
```

Each command and its output is captured in a terminal screenshot under [`screenshots/`](screenshots/), and the plain-text transcript of every step is in [`outputs/`](outputs/). Artifacts uploaded by the workflows are saved in [`artifacts/`](artifacts/).

## Contents

- [01 CI vs CD](#01-ci-vs-cd)
- [02 Pipeline concepts](#02-pipeline-concepts)
- [03 GitHub Actions intro](#03-github-actions-intro)
- [04 Workflows and triggers](#04-workflows-and-triggers)
- [05 Jobs and steps](#05-jobs-and-steps)
- [06 Runners and matrix builds](#06-runners-and-matrix-builds)
- [07 Secrets](#07-secrets)
- [08 Artifacts](#08-artifacts)
- [09 Build and test pipeline (mini project)](#09-build-and-test-pipeline-mini-project)
- [Cleanup](#cleanup)
- [Key learnings](#key-learnings)

**00-setup/01-tools**

![00-setup/01-tools](screenshots/00-setup/01-tools.png)


## 01 CI vs CD

- **CI (continuous integration):** every push is built, linted and tested automatically.
- **Continuous delivery:** a passing build is always ready to deploy.
- **Continuous deployment:** a passing build is deployed automatically.

`ci_simulation.sh` walks through checkout, lint, test and coverage, and `cd_simulation.sh` walks through artifact, deploy and verify.

```powershell
bash ci_simulation.sh
bash cd_simulation.sh
```

**01-ci-vs-cd/01-simulations**

![01-ci-vs-cd/01-simulations](screenshots/01-ci-vs-cd/01-simulations.png)


## 02 Pipeline concepts

A pipeline is made of stages, and stages contain steps. Stages run in order and the pipeline stops at the first failure.

```powershell
Get-Content pipeline.yaml
bash pipeline_stages.sh
```

**02-pipeline-concepts/01-stages-part1**

![02-pipeline-concepts/01-stages-part1](screenshots/02-pipeline-concepts/01-stages-part1.png)

**02-pipeline-concepts/01-stages-part2**

![02-pipeline-concepts/01-stages-part2](screenshots/02-pipeline-concepts/01-stages-part2.png)


## 03 GitHub Actions intro

```powershell
act -l      # list workflows/jobs that GitHub would see in .github/workflows
act push    # simulate a push event
```

`Hello World / say-hello` printed `Hello from GitHub Actions` and finished with **Job succeeded**.

**03-github-actions-intro/01-hello**

![03-github-actions-intro/01-hello](screenshots/03-github-actions-intro/01-hello.png)


## 04 Workflows and triggers

| File | Trigger | Run with |
| :--- | :--- | :--- |
| `push-trigger.yml` | `push` | `act push -W push-trigger.yml` |
| `pr-trigger.yml` | `pull_request` | `act pull_request -W pr-trigger.yml` |
| `workflow-dispatch.yml` | `workflow_dispatch` with inputs | `act workflow_dispatch -W workflow-dispatch.yml --input environment=staging --input run_smoke_tests=true` |
| `schedule-cron.yml` | `schedule: '0 0 * * *'` | `act schedule -W schedule-cron.yml` |
| `path-filter.yml` | `push` with `paths` / `paths-ignore` | `act -l -W path-filter.yml` |
| `.github/workflows/build.yml` | `push`/`pull_request` on `main` | `act push -n` (dry run) |

All four runnable triggers ended with **Job succeeded**. `build.yml` was run as a dry run (`-n`) because this folder has no `requirements.txt` or tests for its `pip install` and `pytest` steps to use. The full build-and-test version is exercise 09.

**04-workflows/01-triggers**

![04-workflows/01-triggers](screenshots/04-workflows/01-triggers.png)

**04-workflows/02-run-push-and-pr**

![04-workflows/02-run-push-and-pr](screenshots/04-workflows/02-run-push-and-pr.png)

**04-workflows/03-run-dispatch-and-schedule**

![04-workflows/03-run-dispatch-and-schedule](screenshots/04-workflows/03-run-dispatch-and-schedule.png)

**04-workflows/04-build-dry-run**

![04-workflows/04-build-dry-run](screenshots/04-workflows/04-build-dry-run.png)


## 05 Jobs and steps

- `jobs-steps.yml`: `test` has `needs: build`, so it waits for `build`.
- `sequential-jobs.yml`: build → test → deploy, chained with `needs`.
- `parallel-jobs.yml`: the lint, unit-test and vulnerability-scan jobs have no `needs`, so they start at the same time.
- `multiline-steps.yml`: multi-line `run: |` blocks and `env:`.

**Bug found in `conditional-steps.yml`.** act rejected the file with `yaml: line 22: mapping values are not allowed in this context`. Line 22 is an unquoted value containing `": "`:

```yaml
run: echo "Workflow finished with job status: ${{ job.status }}"
```

YAML parses `status:` as the start of a nested mapping. Quoting the whole value fixes it ([fixes/conditional-steps-fixed.yml](fixes/conditional-steps-fixed.yml)):

```yaml
run: 'echo "Workflow finished with job status: ${{ job.status }}"'
```

GitHub would reject the original file in the same way, so the workflow would never run.

With the fix, the `if:` conditions behave as intended:

| Event | Build step | Deploy step (`if: github.ref == 'refs/heads/main'`) | Notification (`if: always()`) |
| :--- | :--- | :--- | :--- |
| push to `main` | runs | **runs**: `Production deployment triggered for commit 2c57c9a…` | runs |
| push to `develop` (`-e fixes/push-develop-event.json`) | runs | **skipped** | runs |

All other jobs in this folder ended with **Job succeeded**.

**05-jobs-steps/01-needs**

![05-jobs-steps/01-needs](screenshots/05-jobs-steps/01-needs.png)

**05-jobs-steps/02-sequential-jobs**

![05-jobs-steps/02-sequential-jobs](screenshots/05-jobs-steps/02-sequential-jobs.png)

**05-jobs-steps/03-parallel-jobs**

![05-jobs-steps/03-parallel-jobs](screenshots/05-jobs-steps/03-parallel-jobs.png)

**05-jobs-steps/04-conditional-and-multiline**

![05-jobs-steps/04-conditional-and-multiline](screenshots/05-jobs-steps/04-conditional-and-multiline.png)

**05-jobs-steps/05-conditional-fix**

![05-jobs-steps/05-conditional-fix](screenshots/05-jobs-steps/05-conditional-fix.png)

**05-jobs-steps/06-conditional-on-develop**

![05-jobs-steps/06-conditional-on-develop](screenshots/05-jobs-steps/06-conditional-on-develop.png)


## 06 Runners and matrix builds

- `matrix-demo.yml` ran one job per Python version (3.10 and 3.11).
- `matrix-build.yml` ran 3.9, 3.10 and 3.11 with `fail-fast: false`. `setup-python` downloaded each version, and all three jobs succeeded.
- `multi-os-matrix.yml` and `self-hosted-runner.yml` were listed, not run. act can only emulate Linux runners, and `runs-on: [self-hosted, linux, gpu]` needs a registered self-hosted machine. The listing shows the labels a runner must have.

**06-runners/01-matrix-part1**

![06-runners/01-matrix-part1](screenshots/06-runners/01-matrix-part1.png)

**06-runners/01-matrix-part2**

![06-runners/01-matrix-part2](screenshots/06-runners/01-matrix-part2.png)

**06-runners/01-matrix-part3**

![06-runners/01-matrix-part3](screenshots/06-runners/01-matrix-part3.png)

**06-runners/02-matrix-build-part1**

![06-runners/02-matrix-build-part1](screenshots/06-runners/02-matrix-build-part1.png)

**06-runners/02-matrix-build-part2**

![06-runners/02-matrix-build-part2](screenshots/06-runners/02-matrix-build-part2.png)

**06-runners/02-matrix-build-part3**

![06-runners/02-matrix-build-part3](screenshots/06-runners/02-matrix-build-part3.png)

**06-runners/02-matrix-build-part4**

![06-runners/02-matrix-build-part4](screenshots/06-runners/02-matrix-build-part4.png)

**06-runners/03-labels**

![06-runners/03-labels](screenshots/06-runners/03-labels.png)


## 07 Secrets

```powershell
act push -W .github\workflows\secrets-demo.yml -s GITHUB_TOKEN=local-dummy-token
act push -W deploy-with-secrets.yml -s DOCKER_USERNAME=student -s DOCKER_PASSWORD=S3cr3t-Pa55w0rd
act push -W environment-secrets.yml -s PROD_API_KEY=prod-key-123
```

- `secrets-demo` printed `[PASS] GITHUB_TOKEN is available and automatically provided`.
- In `deploy-with-secrets`, the secret values are replaced with `***` in the log, the same masking GitHub does.
- On GitHub, these values come from *Settings → Secrets and variables → Actions*, or from an environment's secrets for `environment: production`, and never live in the YAML.

**07-secrets/01-github-token**

![07-secrets/01-github-token](screenshots/07-secrets/01-github-token.png)

**07-secrets/02-masking**

![07-secrets/02-masking](screenshots/07-secrets/02-masking.png)

**07-secrets/03-environment-secrets**

![07-secrets/03-environment-secrets](screenshots/07-secrets/03-environment-secrets.png)


## 08 Artifacts

```powershell
act push -W .github\workflows\artifacts-demo.yml --artifact-server-path ..\homework\artifacts\08-artifacts-demo
act push -W upload-download-artifacts.yml --artifact-server-path ..\homework\artifacts\08-upload-download
act push -W test-report-artifact.yml --artifact-server-path ..\homework\artifacts\08-test-report
```

- Upload worked, and so did upload in one job followed by download in a later job.
- The uploaded zips are in [`artifacts/`](artifacts/), for example `sample-artifact.zip`, `build-package` and `test-results.zip`.

**08-artifacts/01-upload**

![08-artifacts/01-upload](screenshots/08-artifacts/01-upload.png)

**08-artifacts/02-upload-download-part1**

![08-artifacts/02-upload-download-part1](screenshots/08-artifacts/02-upload-download-part1.png)

**08-artifacts/02-upload-download-part2**

![08-artifacts/02-upload-download-part2](screenshots/08-artifacts/02-upload-download-part2.png)

**08-artifacts/03-test-report-part1**

![08-artifacts/03-test-report-part1](screenshots/08-artifacts/03-test-report-part1.png)

**08-artifacts/03-test-report-part2**

![08-artifacts/03-test-report-part2](screenshots/08-artifacts/03-test-report-part2.png)


## 09 Build and test pipeline (mini project)

**Local run first** (README step 6):

```powershell
pip install -r requirements.txt
flake8 app.py tests/
python -m pytest tests/ --junitxml=test-results/results.xml --cov=app --cov-report=term-missing
```

Result: flake8 is clean, **4 passed**, and `app.py` has 100% coverage.

**Pipeline** (`.github/workflows/ci.yml`): `lint` → `test` (`needs: lint`) → upload `test-results` and `coverage-report`.

| Run | lint | test | Notes |
| :--- | :--- | :--- | :--- |
| Original code | ✅ | ✅ `4 passed` | Both artifacts uploaded to `artifacts/09-ci` |
| `add()` broken (`return a - b`) | ✅ | ❌ `FAILED tests/test_app.py::test_add - assert -1 == 5` | CI caught the bug; artifacts still uploaded (`if: always()`) |
| Reverted | ✅ | ✅ `4 passed` | Pipeline green again |

The failing-test run used a copy of the folder (`homework/failing-test-demo`, deleted afterwards), so the course code was never changed.

Note: the `pip cache` / `tar` warnings come from `setup-python`'s `cache: pip` option, which needs GitHub's cache service. They don't affect the result.

**09-build-test-pipeline/01-local-run**

![09-build-test-pipeline/01-local-run](screenshots/09-build-test-pipeline/01-local-run.png)

**09-build-test-pipeline/02-ci-pipeline-part1**

![09-build-test-pipeline/02-ci-pipeline-part1](screenshots/09-build-test-pipeline/02-ci-pipeline-part1.png)

**09-build-test-pipeline/02-ci-pipeline-part2**

![09-build-test-pipeline/02-ci-pipeline-part2](screenshots/09-build-test-pipeline/02-ci-pipeline-part2.png)

**09-build-test-pipeline/02-ci-pipeline-part3**

![09-build-test-pipeline/02-ci-pipeline-part3](screenshots/09-build-test-pipeline/02-ci-pipeline-part3.png)

**09-build-test-pipeline/02-ci-pipeline-part4**

![09-build-test-pipeline/02-ci-pipeline-part4](screenshots/09-build-test-pipeline/02-ci-pipeline-part4.png)

**09-build-test-pipeline/02-ci-pipeline-part5**

![09-build-test-pipeline/02-ci-pipeline-part5](screenshots/09-build-test-pipeline/02-ci-pipeline-part5.png)

**09-build-test-pipeline/03-break-the-build**

![09-build-test-pipeline/03-break-the-build](screenshots/09-build-test-pipeline/03-break-the-build.png)

**09-build-test-pipeline/04-ci-fails-part1**

![09-build-test-pipeline/04-ci-fails-part1](screenshots/09-build-test-pipeline/04-ci-fails-part1.png)

**09-build-test-pipeline/04-ci-fails-part2**

![09-build-test-pipeline/04-ci-fails-part2](screenshots/09-build-test-pipeline/04-ci-fails-part2.png)

**09-build-test-pipeline/04-ci-fails-part3**

![09-build-test-pipeline/04-ci-fails-part3](screenshots/09-build-test-pipeline/04-ci-fails-part3.png)

**09-build-test-pipeline/04-ci-fails-part4**

![09-build-test-pipeline/04-ci-fails-part4](screenshots/09-build-test-pipeline/04-ci-fails-part4.png)

**09-build-test-pipeline/05-revert-and-pass-part1**

![09-build-test-pipeline/05-revert-and-pass-part1](screenshots/09-build-test-pipeline/05-revert-and-pass-part1.png)

**09-build-test-pipeline/05-revert-and-pass-part2**

![09-build-test-pipeline/05-revert-and-pass-part2](screenshots/09-build-test-pipeline/05-revert-and-pass-part2.png)

**09-build-test-pipeline/05-revert-and-pass-part3**

![09-build-test-pipeline/05-revert-and-pass-part3](screenshots/09-build-test-pipeline/05-revert-and-pass-part3.png)

**09-build-test-pipeline/05-revert-and-pass-part4**

![09-build-test-pipeline/05-revert-and-pass-part4](screenshots/09-build-test-pipeline/05-revert-and-pass-part4.png)

**09-build-test-pipeline/04-ci-fails-part5**

![09-build-test-pipeline/04-ci-fails-part5](screenshots/09-build-test-pipeline/04-ci-fails-part5.png)

**09-build-test-pipeline/05-revert-and-pass-part5**

![09-build-test-pipeline/05-revert-and-pass-part5](screenshots/09-build-test-pipeline/05-revert-and-pass-part5.png)


## Cleanup

act removes its job containers after each run. The local test outputs (`test-results`, `.coverage`, caches) and the failing-test copy were deleted. Nothing was pushed to GitHub.

**cleanup/01-cleanup**

![cleanup/01-cleanup](screenshots/cleanup/01-cleanup.png)


## Key learnings

- A workflow is triggered by **events** (`push`, `pull_request`, `schedule`, `workflow_dispatch`). Jobs run on **runners**, and each job is a list of **steps** (`uses:` for an action, `run:` for a shell command).
- Jobs run **in parallel** by default. `needs:` makes them run in order and passes failures down the chain.
- A **matrix** fans one job out over versions or OSes. `fail-fast: false` lets the remaining matrix jobs finish after one fails.
- **Secrets** are injected at runtime and masked in logs. Never hard-code them.
- **Artifacts** move files between jobs and keep reports after the run (retention days).
- **CI catches regressions:** a one-character bug failed the pipeline before it could reach anyone else.
