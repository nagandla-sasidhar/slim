---
skill_set: security-auditor
model: claude-opus-4
version: "1.2.0"
classification: internal
---

# Skills Reference: **SecurityAudit Agent** ![status](https://img.shields.io/badge/status-beta-orange)

> **Warning**: This agent has destructive read capabilities. It can access secrets, credentials, and sensitive configuration. **Never** run it on systems you do not own or have written authorization to audit.

---

## Tool Inventory

### Static Analysis Tools

| Tool | Signature | Description | Latency |
|------|-----------|-------------|---------|
| `sast_scan` | `(repo: str, ruleset: str) -> SastReport` | Run *Semgrep* static analysis | ~30s |
| `secret_scan` | `(repo: str) -> list[SecretFinding]` | Find leaked credentials with **TruffleHog** | ~20s |
| `dep_audit` | `(manifest: str) -> list[CVEFinding]` | Check `package.json`/`requirements.txt` for **known CVEs** | ~10s |
| `iac_lint` | `(dir: str, tool: str) -> IacReport` | Lint **Terraform** or **CloudFormation** for misconfigs | ~15s |

### Dynamic Analysis Tools

- **`port_scan(host, ports)`** — Run **nmap** TCP scan on *host*. Only use with `authorized=True`.
- **`ssl_check(host)`** — Check TLS certificate chain, expiry, and cipher suite against [Mozilla Guidelines](https://wiki.mozilla.org/Security/Server_Side_TLS)
- **`header_audit(url)`** — Check HTTP response headers against [OWASP Secure Headers](https://owasp.org/www-project-secure-headers/)
- **`sqli_probe(url, params)`** — Test for SQL injection using **sqlmap** in `--level=1` mode

### Reporting Tools

- `report_html(findings, template)` — Generate an **HTML** report from a `list[Finding]`
- `report_sarif(findings)` — Emit [SARIF](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html) JSON for GitHub Advanced Security integration
- `ticket_create(title, body, severity, tracker)` — Open a ticket in Jira or GitHub Issues

---

## Skill: Full Repository Audit

**Trigger phrase**: "audit this repo" or "security scan"

### Steps

1. Call `secret_scan(repo)` — **block immediately** if any `HIGH` severity finding is returned; do not proceed until it is resolved
2. Call `sast_scan(repo, ruleset="p/owasp-top-10")` and collect findings
3. Identify the dependency manifest (look for `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`)
4. Call `dep_audit(manifest)` for each manifest found
5. If an `infra/` or `terraform/` directory exists, call `iac_lint(dir, tool="terraform")`
6. Aggregate all findings into a `list[Finding]`
7. Call `report_html(findings, template="executive")` and `report_sarif(findings)`
8. For any **CRITICAL** finding, call `ticket_create(severity="critical")` automatically
9. For **HIGH** findings, list them and ask the user if tickets should be opened

### Severity Mapping

| Severity | Action | SLA |
|----------|--------|-----|
| `CRITICAL` | Block CI, auto-ticket | **Immediate** |
| `HIGH` | Flag in report, prompt for ticket | 24 hours |
| `MEDIUM` | Include in report | 7 days |
| `LOW` | Informational | Best effort |
| `INFO` | Suppress from summary | — |

---

## Skill: Dependency Vulnerability Triage

**Purpose**: Help developers understand and prioritize CVE findings.

For each CVE returned by `dep_audit`:

1. Look up the CVE on [NVD](https://nvd.nist.gov/) using `cve_lookup(cve_id)`
2. Determine if the **vulnerable code path is reachable** in this project
3. Check if a **fixed version** exists in the package registry
4. Recommend one of:
   - **Upgrade** — if a fix exists and upgrade is straightforward
   - **Patch** — if no fix exists but a workaround is documented
   - **Accept risk** — if the vulnerable code path is unreachable (document reasoning)
   - **Remove** — if the dependency is unused

---

## Skill: Infrastructure Misconfiguration Review

**Purpose**: Find insecure cloud configuration in Terraform/CloudFormation.

Focus areas:

- **S3 buckets**: public access, ACL settings, encryption at rest
- **Security groups**: `0.0.0.0/0` ingress on non-HTTP/S ports
- **IAM**: overly permissive policies, `*` actions, inline policies
- **RDS**: public accessibility, unencrypted storage, old engine versions
- **Secrets**: hardcoded secrets in resource definitions or `user_data`

For each finding, output:

```
Resource: aws_s3_bucket.user_data
Issue: Bucket is publicly accessible via ACL
Severity: HIGH
Fix: Set acl = "private" and enable block_public_access
Reference: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket
```

---

## Constraints

- **Never** run `port_scan` without `authorized=True` explicitly set
- **Never** run `sqli_probe` against a production URL without written authorization
- **Always** log the start time, scope, and completion of every scan
- Do **not** store secrets found by `secret_scan` in any log or output file — report only the file path and line number
- Findings containing **PII** (emails, phone numbers, SSNs) must be redacted before inclusion in reports shared outside the security team
