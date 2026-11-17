# Interview notes: CI/CD pipeline

## 60-second pitch

"I built a CI/CD pipeline in GitHub Actions for a containerised Python service. Every
pull request is linted and tested on a Python version matrix. On merge to main, the
image is built, scanned with Trivy, tagged with the commit SHA and pushed to GHCR. A
separate deploy workflow assumes an AWS role through OIDC, registers a new ECS task
definition and waits for the service to stabilise, behind a manual approval gate."

## Design decisions you should be able to defend

- **Why SHA tags, not just `latest`?** Immutable, traceable to a commit, enables exact
  rollbacks. `latest` is a convenience pointer only.
- **Why OIDC instead of access keys?** No long-lived secrets to leak or rotate; the role
  trust policy can be restricted to this repo, branch and environment.
- **Why scan before push?** Fail fast: a vulnerable image never reaches the registry.
- **Why a separate deploy workflow?** CI runs on every PR with read-only permissions;
  deploy needs cloud credentials, so it is isolated, gated and runs only for main.
- **Why `concurrency` on deploy?** Prevents two deployments racing on the same service.
- **Why multi-stage and non-root?** Smaller attack surface and image size; limits impact
  of a container escape or RCE.

## Likely questions

1. **How would you roll back?** Re-run the deploy workflow with `workflow_dispatch` and a
   previous `sha-xxxx` tag, or `aws ecs update-service` to the previous task definition
   revision. With ECS deployment circuit breaker enabled it rolls back automatically.
2. **Rolling vs blue/green vs canary?** This uses ECS rolling updates. Blue/green via
   CodeDeploy gives instant cutback; canary shifts a small % of traffic first.
3. **How do you speed up the pipeline?** Dependency and Docker layer caching (already
   used), parallel jobs, path filters, only building on changed code.
4. **How do you handle secrets?** GitHub environment secrets for CI-only values; AWS
   Secrets Manager / SSM for runtime secrets, injected by ECS, never baked into images.
5. **What would you add next?** SBOM generation, image signing with cosign, DAST smoke
   tests after deploy, Slack notifications, Dependabot for actions and base images.
6. **`workflow_run` vs `needs`?** `workflow_run` decouples CI from CD so deploy can be
   re-triggered independently; the trade-off is it runs in the default-branch context.
7. **How do you stop a failed deploy hurting users?** Health checks on the load balancer,
   minimum healthy percent, circuit breaker, and the approval gate.

## Things to be honest about

- The deploy job needs an ECS service to exist; it is written and reviewed but only runs
  once you wire up the AWS side. Say so, and explain how you would test it in a sandbox.
