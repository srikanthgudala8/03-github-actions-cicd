> **Phase 3 of the 60-day journey** (Days 19-26). Day-by-day plan: **[LEARNING.md](LEARNING.md)**.
> Workflow practice files are in `labs/workflows/`. Deploy targets: Azure Container Apps
> (`azure-deploy.yml`) and AWS ECS (`deploy.yml`).

# DevOps CI/CD Pipeline (GitHub Actions + Docker + AWS ECS)

A complete CI/CD pipeline for a small containerised Flask service.

```
 push / PR ──► CI workflow                                   Deploy workflow
              ┌────────────┐   ┌──────────────────────────┐   ┌───────────────────────┐
              │ flake8     │   │ docker build             │   │ OIDC → AWS role       │
              │ pytest     │──►│ Trivy scan (HIGH/CRIT)   │──►│ new ECS task def      │
              │ (py 3.11,  │   │ push to GHCR (main only) │   │ update service, wait  │
              │  3.12)     │   └──────────────────────────┘   │ for stable (approval) │
              └────────────┘                                   └───────────────────────┘
```

## What it demonstrates

| Area | Implementation |
|------|----------------|
| Continuous integration | Lint + unit tests on a Python version matrix, pip caching |
| Container best practice | Multi-stage build, non-root user, healthcheck, `.dockerignore` |
| Supply-chain security | Trivy image scan fails the build on fixable HIGH/CRITICAL CVEs |
| Image tagging | Immutable `sha-<short>` tag per commit, plus `latest` on main |
| Continuous delivery | ECS rolling deploy, gated by a GitHub `production` environment |
| Secrets | No AWS keys in GitHub: short-lived credentials via OIDC |
| Safety | `concurrency` group so two deploys never run at once |

## Run locally

```bash
pip install -r requirements-dev.txt
pytest
docker build -t demo-app .
docker run --rm -p 8080:8080 demo-app
curl localhost:8080/health
```

## Setting up the deploy workflow

CI works as soon as you push. Deployment needs an AWS target:

1. Create an ECS cluster, service and task definition (the sibling
   `04-terraform-azure-aws` project is a good base).
2. Create an IAM role that trusts GitHub OIDC for this repo, with permission for
   `ecs:DescribeTaskDefinition`, `ecs:RegisterTaskDefinition`, `ecs:UpdateService`,
   `ecs:DescribeServices` and `iam:PassRole` for the task roles.
3. In **Settings → Environments**, create `production` and add required reviewers.
4. Under **Settings → Secrets and variables → Actions → Variables**, add:
   `AWS_REGION`, `AWS_DEPLOY_ROLE_ARN`, `ECS_CLUSTER`, `ECS_SERVICE`, `ECS_TASK_FAMILY`.

If the ECS task pulls from GHCR and the package is private, store a pull credential
in AWS Secrets Manager and reference it as `repositoryCredentials` in the task
definition, or make the package public.

## Layout

```
app/                Flask service (+ Prometheus metrics)
tests/              pytest suite
Dockerfile          multi-stage, non-root
.github/workflows/  ci.yml, deploy.yml
INTERVIEW.md        talking points and Q&A for this project
```

## Azure deploy: repository variables

For `.github/workflows/azure-deploy.yml`, set these under **Settings -> Secrets and variables -> Actions -> Variables**:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `CONTAINERAPP_NAME`.
The app registration needs a federated credential for the `production` environment of this repo.
