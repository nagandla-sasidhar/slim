---
name: "SlackBot Agent"
trigger: "@bot"
channel: "#engineering"
---

# **SlackBot Agent** — Quick Reference

## Commands

| Command | Example | What it does |
|---------|---------|--------------|
| `@bot deploy <service> <env>` | `@bot deploy api prod` | Trigger deployment |
| `@bot status <service>` | `@bot status worker` | Show current health |
| `@bot logs <service> <n>` | `@bot logs api 50` | Tail last *n* lines |
| `@bot rollback <service>` | `@bot rollback api` | Roll back last deploy |

## Permissions

**Any engineer** can: `status`, `logs`
**Senior engineer or on-call** only: `deploy`, `rollback`

## Error Messages

- `[AUTH_FAIL]` — you don't have permission; ping `@oncall`
- `[SVC_NOT_FOUND]` — check spelling; run `@bot list-services`
- `[DEPLOY_IN_PROGRESS]` — another deploy is running; **wait** or use `@bot cancel`

See [runbook](https://wiki.internal/slackbot) for full docs.
