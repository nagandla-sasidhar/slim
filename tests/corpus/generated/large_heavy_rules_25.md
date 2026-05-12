---
ruleset: ml-platform-agent
version: "4.1"
enforced: true
last_review: 2025-01-15
owner: platform-team
---

# Rules: **ML Platform Agent** ![enforced](https://img.shields.io/badge/enforced-yes-red)

> **Warning**: These rules are **enforced** — violations will cause the agent to refuse the action and log a policy event. They are not suggestions.

---

## Rule Categories

- [Data Rules](#data-rules)
- [Model Rules](#model-rules)
- [Compute Rules](#compute-rules)
- [Deployment Rules](#deployment-rules)
- [Communication Rules](#communication-rules)

---

## Data Rules

### DR-01: No PII in Training Data

**Status**: `ENFORCED` | **Severity**: `CRITICAL`

*Never* include Personally Identifiable Information in training datasets. This includes:

- Names, email addresses, phone numbers
- Government IDs (SSN, passport, driver's license)
- Financial account numbers
- Medical record identifiers
- IP addresses and device fingerprints linked to individuals

**Check**: Run `pii_scan(dataset)` before any training job. If `pii_scan` returns any findings, **halt** and report to the data-governance channel.

### DR-02: Data Lineage Required

**Status**: `ENFORCED` | **Severity**: `HIGH`

Every dataset used for training or evaluation must have a lineage record in the [Data Catalog](https://catalog.internal/). The record must include:

| Field | Type | Required |
|-------|------|----------|
| `source_name` | string | yes |
| `collection_date` | ISO 8601 | yes |
| `license` | SPDX string | yes |
| `pii_cleared` | bool | yes |
| `consent_mechanism` | string | yes if user data |

**Check**: Call `catalog_lookup(dataset_id)` before training. Fail if no record exists.

### DR-03: Encryption at Rest

**Status**: `ENFORCED` | **Severity**: `HIGH`

All training data stored in S3 must use **SSE-S3** or **SSE-KMS** encryption. Check with:

```bash
aws s3api head-object --bucket $BUCKET --key $KEY \
  --query 'ServerSideEncryption'
```

If the result is `null`, refuse to use the dataset and open a ticket.

---

## Model Rules

### MR-01: Model Card Required Before Registration

**Status**: `ENFORCED` | **Severity**: `HIGH`

Every model registered in the model registry must have a Model Card following the [Hugging Face model card spec](https://huggingface.co/docs/hub/model-cards). Required sections:

1. **Model Description** — what the model does, its architecture
2. **Training Data** — dataset names, sizes, collection period
3. **Evaluation Results** — metrics table with dataset and metric names
4. **Limitations** — known failure modes, demographic gaps
5. **Intended Use** — approved use cases
6. **Out-of-Scope Use** — explicitly prohibited applications

### MR-02: Bias Evaluation Required

**Status**: `ENFORCED` | **Severity**: `HIGH`

Before deployment, run bias evaluation using the configured fairness suite:

```python
from ml_platform.fairness import evaluate_fairness

report = evaluate_fairness(
    model=model,
    eval_dataset=eval_ds,
    protected_attrs=["gender", "age_group", "region"],
    metrics=["demographic_parity", "equalized_odds"],
)
assert report.max_disparity < 0.05, f"Bias threshold exceeded: {report}"
```

If `max_disparity >= 0.05` on any protected attribute, **block deployment** and escalate to the Responsible AI team.

### MR-03: No Shadow Deployments to Production Without Approval

**Status**: `ENFORCED` | **Severity**: `CRITICAL`

Shadow deployments route a percentage of **real production traffic** to the new model. This requires:

- Written approval from the **ML Platform Lead**
- An incident runbook linked in the deployment config
- Monitoring dashboards configured before the shadow period begins

---

## Compute Rules

### CR-01: Spot Instance Preference

**Status**: `ADVISORY` | **Severity**: `LOW`

Training jobs should use **spot instances** where possible. Use on-demand instances only when:
- The job cannot tolerate interruption (e.g., final training run before a deadline)
- The spot market has been unavailable for > 30 minutes in the target AZ

### CR-02: GPU Idle Time Limit

**Status**: `ENFORCED` | **Severity**: `MEDIUM`

Terminate GPU instances that have been idle (GPU utilization < 5%) for more than **30 minutes**. The agent checks every 10 minutes and sends a Slack warning at 20 minutes before terminating.

| Idle Duration | Action |
|---------------|--------|
| 20 min | Warn in `#ml-ops` Slack |
| 30 min | Terminate instance |
| Recurring (3x in 24h) | Flag user to manager |

---

## Deployment Rules

### DP-01: Blue-Green Deployments Required in Production

All production model deployments use **blue-green** strategy:

1. Deploy new model to **green** endpoint (no traffic)
2. Run smoke tests against green
3. Shift **10% of traffic** to green; monitor error rate for 5 min
4. If error rate < baseline: shift **50%**, monitor 5 min
5. If still OK: shift **100%**; decommission blue after 24 h

If error rate spikes at any step, **immediately shift 100% back to blue**.

### DP-02: Rollback Runbook Required

Every deployment must have a rollback runbook stored in `runbooks/rollback-{model_name}.md`. The runbook must include:
- The command to revert to the previous version
- The expected time to complete
- Who to notify

---

## Communication Rules

- **Never** share model weights, training data samples, or evaluation datasets outside the organization
- **Never** acknowledge or deny whether a specific customer's data was used for training
- Report all **CRITICAL** rule violations to `#ml-platform-alerts` within **15 minutes**

---

## Links

- [Data Catalog](https://catalog.internal/) | [Model Registry](https://mlflow.internal/) | [Fairness Toolkit](https://fairness.internal/) | [Responsible AI Policy](https://policy.internal/responsible-ai)
