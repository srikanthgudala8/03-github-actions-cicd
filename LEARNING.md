# Phase 3 - GitHub Actions and CI/CD (Days 19-26)

**Goal:** design, write and debug real pipelines: test, build, scan, publish and deploy,
with secure credentials (OIDC) and approval gates.

**The project in this repo** is a complete working pipeline. Learn by *reading it,
breaking it, and fixing it*. Workflow exercises are in `labs/workflows/` (they live
outside `.github/workflows/` so they do not run until you copy them in).

---

## Day-by-day plan

### Day 19 - Workflow anatomy
- **Learn:** workflows, events, jobs, steps, runners, `uses` vs `run`, contexts (`github.*`, `env.*`), expressions `${{ }}`.
- **Lab:** copy `labs/workflows/01-hello.yml` into `.github/workflows/`, push, read the logs. Add a second job with `needs:` and pass a value between jobs using `outputs`.
- **Done when:** you can read any workflow file top to bottom and say what it does.

### Day 20 - Triggers, matrix, cache, artifacts
- **Learn:** `push`, `pull_request`, `schedule`, `workflow_dispatch`, path filters, `if:` conditions, matrix, caching, artifacts.
- **Lab:** run `labs/workflows/02-matrix-and-cache.yml`. Measure run time with and without cache.
- **Done when:** you can explain why a PR workflow and a main-branch workflow should differ.

### Day 21 - Continuous integration for Python
- **Learn:** lint, test, coverage as quality gates. Branch protection: require the CI check before merge.
- **Lab:** study `.github/workflows/ci.yml` (job `test`). Add a deliberate lint error on a branch, watch the PR fail, then fix it. Turn on branch protection for `main`.
- **Done when:** nobody (including you) can merge a failing PR.

### Day 22 - Build and push Docker images
- **Learn:** `docker/build-push-action`, buildx cache, `docker/metadata-action` tags, GHCR and `GITHUB_TOKEN` permissions.
- **Lab:** study job `build` in `ci.yml`. After a push to `main`, find your image under the repo's **Packages**. Pull it and run it locally.
- **Done when:** every commit produces an image tagged `sha-<short>`.

### Day 23 - Secrets, variables, environments and OIDC
- **Learn:** repository vs environment secrets, variables, environment protection rules, why long-lived cloud keys are a liability, OIDC federation.
- **Lab:** create a `production` environment with a required reviewer. Read `deploy.yml` (AWS) and `azure-deploy.yml` (Azure) and write down how each gets short-lived credentials.
- **Do not:** print secrets in logs or pass them to untrusted PRs (forks).
- **Done when:** you can explain OIDC to an interviewer in 30 seconds.

### Day 24 - Reuse: reusable workflows and composite actions
- **Learn:** `workflow_call`, inputs and secrets, composite actions, DRY across many repos.
- **Lab:** do `labs/workflows/03-reusable-workflow.yml` and `04-composite-action/`. Refactor `ci.yml` to call your reusable workflow.
- **Done when:** the same logic exists in exactly one place.

### Day 25 - Deploy to the cloud
- **Learn:** deployment strategies (rolling, blue/green, canary), health checks, rollbacks, approvals.
- **Azure lab (recommended first):** create an Azure Container App (Terraform in Phase 4 will do this for you, or use the portal now). Create an app registration with a **federated credential** for `repo:<you>/03-github-actions-cicd:environment:production`, give it Contributor on the resource group, set the repo variables listed in the README, run **Deploy to Azure Container Apps**.
- **AWS reading:** `deploy.yml` does the same with ECS. Note the similarities.
- **Done when:** a button click deploys a specific image tag and the workflow verifies `/health`.

### Day 26 - Security scanning and capstone
- **Learn:** shift-left security: Trivy image scan (already in CI), CodeQL (SAST), Dependabot, secret scanning, pinning actions to a SHA, least-privilege `permissions:`.
- **Lab:** enable Dependabot and CodeQL (files are already here), read the Security tab, fix one finding.
- **Capstone:** a PR-to-production pipeline: lint -> test -> build -> scan -> push -> (approval) -> deploy -> smoke test. Add a status badge to the README and record a 2-minute screen capture.

---

## Debugging pipelines
1. Read the **first** red line, not the last.
2. Re-run with debug logging: set secret/variable `ACTIONS_STEP_DEBUG` to `true`.
3. Reproduce locally (`act`, or run the same commands in a container).
4. "Permission denied" pushing a package: check `permissions: packages: write` and package visibility.
5. YAML errors: indentation and quoting, validate with `yamllint`.
6. Works on PR, fails on main (or the reverse): compare `if:` conditions and available secrets.

## Check yourself
1. What is the difference between a job and a step? How do jobs share data?
2. Why use `needs:` and `concurrency:`?
3. Repository secret vs environment secret?
4. How does OIDC replace stored cloud credentials?
5. Why pin third-party actions to a commit SHA?
6. What does `permissions: contents: read` do and why set it?
7. How would you roll back a bad deploy with this pipeline?
