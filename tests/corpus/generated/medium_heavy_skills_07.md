---
title: Skills Reference — DevOps Agent
version: 2.4.1
updated: 2024-11-15
tags: [devops, ci-cd, kubernetes, terraform]
---

# Skills Reference: **DevOps Agent** ![version](https://img.shields.io/badge/v2.4.1-blue)

## Tool Inventory

### Infrastructure Tools

| Tool | Signature | Description |
|------|-----------|-------------|
| `terraform_plan` | `(dir: str) -> PlanResult` | Run `terraform plan` in *dir* |
| `terraform_apply` | `(dir: str, auto_approve: bool) -> ApplyResult` | Apply plan; set `auto_approve=False` for prod |
| `kubectl_apply` | `(manifest: str) -> KubeResult` | Apply a **raw YAML** manifest |
| `kubectl_rollout` | `(deployment: str, ns: str) -> RolloutStatus` | Watch rollout until stable or timeout |

### CI/CD Tools

- **`pipeline_trigger(repo, branch, vars)`** — Trigger a [GitHub Actions](https://docs.github.com/en/actions) workflow
- **`build_image(dockerfile, tag, push)`** — Build and optionally push a Docker image
- **`run_tests(suite, env)`** — Execute a named test suite in an environment

### Monitoring Tools

- `metrics_query(promql)` — Query [Prometheus](https://prometheus.io/docs/querying/basics/) with a PromQL expression
- `log_tail(service, lines, level)` — Tail recent logs from [Loki](https://grafana.com/docs/loki/)
- `alert_silence(matcher, duration)` — Silence an Alertmanager alert matcher for *duration*

---

## Skill: Deploy Service

**Purpose**: Roll out a new container image to a Kubernetes namespace.

**Steps**:
1. Call `build_image(dockerfile="Dockerfile", tag=f"{service}:{version}", push=True)`
2. Patch the `Deployment` manifest with the new image tag
3. Call `kubectl_apply(manifest)` with the patched YAML
4. Call `kubectl_rollout(deployment=service, ns=namespace)` and **wait** for `status=stable`
5. If rollout fails, call `kubectl_rollout` with `undo=True` to **roll back**

> **Never** set `auto_approve=True` for `terraform_apply` in the `prod` environment without an explicit user instruction.

---

## Skill: Cost Audit

**Purpose**: Identify expensive cloud resources.

Steps:
1. Run `metrics_query("sum by(service) (aws_cost_usd_per_hour)")` for the last 7 days
2. Sort results descending
3. Flag any service costing **>$50/hr**
4. Produce a Markdown table of top-10 spenders

---

## Error Taxonomy

| Code | Meaning | Action |
|------|---------|--------|
| `PLAN_DIFF_DESTROY` | Terraform wants to *destroy* resources | **Halt**, ask user |
| `IMAGE_PUSH_FAIL` | Registry unreachable | Retry up to **3x** with 10s backoff |
| `ROLLOUT_TIMEOUT` | Pods not ready in 5 min | Roll back, send alert |
| `METRICS_EMPTY` | No data returned | Log `[WARN]`, continue |

See also: [Terraform docs](https://developer.hashicorp.com/terraform/docs) | [kubectl cheatsheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
