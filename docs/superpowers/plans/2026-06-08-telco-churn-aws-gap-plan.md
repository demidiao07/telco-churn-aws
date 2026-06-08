# Telco Churn AWS Remaining Work Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the current telco churn prototype into a complete, reproducible AWS cloud engineering project submission that satisfies the course requirements for data storage, training, deployment, monitoring, security, documentation, and presentation artifacts.

**Architecture:** Keep the current simple shape of the project: preprocess locally or on EC2, train a scikit-learn Random Forest model, store artifacts in S3, and serve inference through FastAPI on EC2. The remaining work is mostly hardening and packaging: make the pipeline reproducible, wire the code to AWS instead of local-only paths, add configuration and observability, document the deployment, and produce the missing submission artifacts.

**Tech Stack:** Python, pandas, scikit-learn, FastAPI, joblib, AWS EC2, AWS S3, CloudWatch, IAM, GitHub

---

## Current State Summary

### What already exists

- Raw data and processed CSV artifacts are present under `data/raw/` and `data/processed/`.
- A basic preprocessing script exists in [preprocess.py](/Users/evelynxu/Documents/cloud%20final%20proj/repo/src/preprocess.py:1).
- A basic training script exists in [train.py](/Users/evelynxu/Documents/cloud%20final%20proj/repo/src/train.py:1).
- A minimal FastAPI app exists in [app.py](/Users/evelynxu/Documents/cloud%20final%20proj/repo/src/app.py:1).
- EDA work exists in [eda.ipynb](/Users/evelynxu/Documents/cloud%20final%20proj/repo/notebooks/eda.ipynb).
- Screenshots exist for EC2, S3, CloudWatch, FastAPI, and an architecture diagram under `docs/`.

### Gaps confirmed from the repo

- [README.md](/Users/evelynxu/Documents/cloud%20final%20proj/repo/README.md:1) is effectively empty, so there is no setup guide, architecture explanation, dataset citation, deployment guide, or submission narrative.
- `src/train.py` is not fully runnable as committed: it tries to save to `models/model.pkl`, but the `models/` directory is gitignored and not created first, so training currently fails at save time.
- `src/app.py` assumes `models/model.pkl` already exists locally and has no request schema validation, feature ordering enforcement, logging, health checks, or error handling.
- `requirements.txt` is incomplete for deployment because it does not include `fastapi` or `uvicorn`, and dependency versions are not pinned.
- There is no infrastructure-as-code, no deployment script, no Dockerfile, no systemd/nginx setup, and no CI pipeline.
- There is no configuration layer for bucket names, regions, model paths, ports, or environment-specific settings.
- There is no real secrets/config handling pattern beyond `.gitignore`.
- There is no automated S3 upload/download flow in code even though the architecture and screenshots imply S3-backed artifacts.
- There are no tests, no linter/formatter config, and no quality gates.
- There is no explicit AWS cost estimate artifact, no project timeline artifact, no final report artifact, and no presentation source in the repo.

---

## Priority Order

1. Make the local ML pipeline reproducible and runnable end to end.
2. Move data/model artifact handling from manual local steps to explicit S3-backed code paths.
3. Harden and document the API deployment on EC2.
4. Add logging, monitoring, config management, and basic security controls.
5. Produce the missing project deliverables: README, cost estimate, timeline, report, and presentation support files.

---

## Remaining Work Plan

### Phase 1: Repository Packaging And Submission Readiness

**Outcome:** The repo becomes understandable and gradable by itself.

- [ ] Replace the empty README with a full project narrative.
  - Include: problem statement, dataset source, architecture overview, AWS services used, setup steps, training steps, deployment steps, API usage example, monitoring evidence, and known limitations.
  - Files: `README.md`, `docs/architecture-diagram.png`, `docs/*.png`

- [ ] Add a `docs/` submission index.
  - Create a single markdown file that points to the architecture diagram, EC2 screenshot, S3 screenshot, CloudWatch screenshot, FastAPI screenshot, and any final report/presentation files.
  - Files: `docs/submission-checklist.md`

- [ ] Add the missing planning artifacts required by the course.
  - Include a timeline and an AWS cost estimate export or screenshot.
  - Files: `docs/project-timeline.md`, `docs/aws-cost-estimate.png` or `docs/aws-cost-estimate.pdf`

- [ ] Add dataset provenance.
  - Cite the Telco Customer Churn source and describe why it was chosen.
  - Files: `README.md`, optionally `docs/data-source.md`

### Phase 2: Make The Existing Code Actually Reproducible

**Outcome:** A grader can clone the repo and run preprocess -> train -> serve without hidden manual fixes.

- [ ] Fix the training save path issue.
  - `src/train.py` must create the `models/` directory before calling `joblib.dump(...)`.
  - Files: `src/train.py`, optionally add `models/.gitkeep`

- [ ] Refactor scripts into callable functions plus CLI entry points.
  - Right now `src/train.py` executes on import and `src/app.py` loads the model at import time. Split them into reusable functions for train/load/predict.
  - Files: `src/preprocess.py`, `src/train.py`, `src/app.py`

- [ ] Pin and complete dependencies.
  - Add the missing web-serving packages and pin versions for reproducibility.
  - Files: `requirements.txt`

- [ ] Add a local run guide and smoke commands.
  - Example flow: install deps, preprocess data, train model, run API, call `/predict`.
  - Files: `README.md`

- [ ] Add a sample prediction payload.
  - Because the API currently accepts an untyped raw dict, provide at least one valid JSON example that matches the engineered feature columns.
  - Files: `README.md`, optionally `examples/sample_request.json`

### Phase 3: Add Proper AWS Data And Artifact Integration

**Outcome:** The project clearly uses AWS as the primary store for datasets and artifacts, not just local files plus screenshots.

- [ ] Add explicit S3 upload/download utilities.
  - Support raw data upload, processed data upload, model artifact upload, and optional log upload.
  - Files: create `src/aws_io.py` or `src/storage.py`

- [ ] Parameterize S3 bucket names and prefixes.
  - The current architecture implies prefixes such as `raws/`, `processed/`, `models/`, and `logs/`. Make them configurable.
  - Files: create `config/config.yaml` or `.env.example`, plus loader code in `src/`

- [ ] Update preprocessing and training flows to optionally read/write through S3.
  - At minimum, processed datasets and the trained model should be pushed to S3 as part of the standard workflow.
  - Files: `src/preprocess.py`, `src/train.py`

- [ ] Decide on the single source of truth for inference artifacts.
  - Recommendation: EC2 startup should pull the latest `model.pkl` from S3 into a known local path, then FastAPI should load that path.
  - Files: `src/app.py`, deployment scripts, README

### Phase 4: Harden The Inference Service

**Outcome:** The API becomes deployable, testable, and less fragile.

- [ ] Add request schema validation with Pydantic models.
  - The current `predict(features: dict)` endpoint does not validate fields or types.
  - Files: `src/app.py`

- [ ] Enforce feature ordering and preprocessing compatibility.
  - The model was trained on one-hot encoded columns, but the API currently assumes the caller already sends the post-encoding schema. That is not practical for real use.
  - Recommended fix: save preprocessing metadata and run the same preprocessing path inside inference.
  - Files: `src/preprocess.py`, `src/train.py`, `src/app.py`

- [ ] Add health and version endpoints.
  - Useful for deployment validation and grading demos.
  - Files: `src/app.py`

- [ ] Add structured logging around requests and predictions.
  - Log startup, model-load success/failure, request IDs, prediction latency, and errors.
  - Files: `src/app.py`

- [ ] Add a proper application start command.
  - Include `uvicorn` invocation or a process manager command in the README and deployment notes.
  - Files: `README.md`, optional service file under `deploy/`

### Phase 5: Add Deployment Automation For EC2

**Outcome:** The EC2 deployment becomes repeatable instead of manual.

- [ ] Add a deployment directory.
  - Include a shell script or setup steps for instance bootstrap, dependency install, code checkout, model sync, and API startup.
  - Files: create `deploy/setup_ec2.sh`, `deploy/run_api.sh`

- [ ] Capture EC2 service management.
  - Recommended: add a `systemd` unit file so the API restarts automatically after reboot.
  - Files: create `deploy/telco-churn-api.service`

- [ ] Document security group and port assumptions.
  - Clarify what port the API listens on, which inbound rules are required, and whether the endpoint is public or behind a reverse proxy.
  - Files: `README.md`, optionally `docs/deployment-notes.md`

- [ ] Decide whether to stay on raw EC2 or switch to containerized deployment.
  - For this class, staying on EC2 is acceptable and simpler, but then the repo should show a clean operational procedure.
  - Deliverable: document the decision in `README.md`.

### Phase 6: Add Configuration Management, Logging, And Monitoring

**Outcome:** The repo meets the course requirement around secure configuration and operational visibility.

- [ ] Introduce environment-based configuration.
  - Use environment variables or a non-secret config file for bucket name, AWS region, local artifact paths, host, port, and log level.
  - Files: create `.env.example` or `config/config.yaml`, add loader module

- [ ] Make the AWS credential story explicit.
  - Document use of an EC2 IAM role rather than hardcoded access keys.
  - Files: `README.md`, `docs/deployment-notes.md`

- [ ] Add application logs in CloudWatch.
  - Current screenshot only shows EC2 CPUUtilization. Add actual API/application logs or custom metrics if possible.
  - Files: deployment docs, possibly `src/app.py`

- [ ] Add at least one alarm with a reasoned threshold.
  - Examples: CPU too high, instance status check failed, low disk space, repeated API failures.
  - Files: `docs/cloudwatch-alarm.png`, `docs/submission-checklist.md`

- [ ] Add optional prediction request logging.
  - Even simple JSON logs to a file streamed by CloudWatch Agent would strengthen the cloud engineering story.
  - Files: `src/app.py`, deployment scripts

### Phase 7: Add Good Coding Practices And Validation

**Outcome:** The repo satisfies the coding-quality requirement and becomes easier to demo.

- [ ] Add basic tests.
  - Cover: preprocessing shape/columns, training output path, and one API prediction smoke test.
  - Files: create `tests/test_preprocess.py`, `tests/test_train.py`, `tests/test_app.py`

- [ ] Add formatting and linting config.
  - At minimum: `black`, `ruff`, or `flake8`.
  - Files: `requirements.txt`, create `pyproject.toml` or tool config

- [ ] Add `.gitignore` cleanup and artifact policy.
  - Decide what belongs in git versus S3 versus generated-at-runtime.
  - Files: `.gitignore`, `README.md`

- [ ] Remove stray `.DS_Store` files from version control.
  - Files affected: `data/.DS_Store`, `docs/.DS_Store`, root `.DS_Store`

### Phase 8: Finish The Missing Final Deliverables

**Outcome:** The team has everything needed for grading and presentation.

- [ ] Produce a polished architecture diagram source file.
  - The screenshot is helpful, but the course brief explicitly references a diagrams.net architecture artifact.
  - Files: create `docs/architecture-diagram.drawio`

- [ ] Add a final written report or project summary.
  - Cover objectives, architecture, preprocessing, model performance, deployment, monitoring, cost, and lessons learned.
  - Files: `docs/final-report.md` or `docs/final-report.pdf`

- [ ] Package the presentation evidence.
  - Include the slide deck or exported PDF if available.
  - Files: `presentation/` or `docs/presentation.pdf`

- [ ] Build a submission ZIP checklist.
  - List exactly what gets submitted: code, notebook, scripts, screenshots, report, and presentation.
  - Files: `docs/submission-checklist.md`

---

## Suggested Execution Order By Day

### Day 1

- [ ] Fix `train.py` and complete `requirements.txt`
- [ ] Expand `README.md`
- [ ] Add `.env.example` or config file
- [ ] Add S3 utility module

### Day 2

- [ ] Wire preprocess/train to S3
- [ ] Refactor API input handling and schema validation
- [ ] Add deployment scripts for EC2

### Day 3

- [ ] Add logging and CloudWatch documentation
- [ ] Add tests and formatter/linter config
- [ ] Produce cost estimate and timeline docs

### Day 4

- [ ] Finalize report, architecture source file, and presentation materials
- [ ] Do a full end-to-end demo run and capture final screenshots

---

## Highest-Risk Items

- The API is not truly usable yet because inference expects already-encoded feature columns rather than raw customer attributes.
- The AWS usage is only partially captured in code; right now the repo mostly shows local scripts plus AWS screenshots.
- The project could lose points on cloud engineering depth unless S3 integration, deployment procedure, and monitoring are made explicit and reproducible.
- The empty README and missing cost/timeline/report artifacts make the current submission under-documented even if the demo worked live.

---

## Definition Of Done

The project is ready when all of the following are true:

- A grader can follow `README.md` to run preprocessing, training, deployment, and prediction.
- Raw data, processed data, and model artifacts have a documented S3 flow.
- The FastAPI app validates inputs and serves predictions reliably on EC2.
- Configuration is environment-driven and does not require hardcoded secrets.
- CloudWatch evidence includes more than basic CPU metrics.
- The repo includes the architecture artifact, cost estimate, timeline, report, and presentation support files.
- Tests and formatting/linting steps are documented and pass locally.
