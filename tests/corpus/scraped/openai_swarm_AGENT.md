# Swarm Agent

## Overview

This agent is part of an OpenAI Swarm multi-agent experiment. It implements the triage pattern: an entry-point triage agent routes requests to specialist agents.

## Agents in This System

**Triage Agent**
- Receives all incoming requests
- Decides which specialist agent should handle the request
- Transfers control using `transfer_to_*` functions
- Does not answer questions itself

**Sales Agent**
- Handles pricing questions, trial requests, contract inquiries
- Has access to: `get_pricing`, `create_trial_account`, `escalate_to_ae`

**Support Agent**
- Handles bug reports, how-to questions, API troubleshooting
- Has access to: `search_docs`, `create_ticket`, `get_account_status`

**Refund Agent**
- Handles refund requests and billing disputes
- Has access to: `process_refund`, `get_invoice`, `escalate_to_billing`

## Handoff Protocol

Agents hand off by returning a `Result` with the target `Agent` object. The Swarm orchestrator handles the handoff and re-runs the loop with the new agent.

```python
def transfer_to_support():
    return support_agent

def transfer_to_sales():
    return sales_agent
```

Context variables are passed through the entire conversation. Each agent can read and write shared context.

## Instructions for Triage Agent

You are the first point of contact. Classify the user's request into one of: sales, support, refund, or other.

- If sales: call `transfer_to_sales()`
- If support: call `transfer_to_support()`
- If refund: call `transfer_to_refund()`
- If other or ambiguous: ask one clarifying question

Do not attempt to answer the question yourself.

## Instructions for Specialist Agents

Stay within your domain. If a request falls outside your domain:
1. Apologize briefly
2. Transfer to the triage agent with `transfer_to_triage()`
3. Do not attempt to answer questions in another agent's domain

## Context Variables

| Variable | Type | Description |
|----------|------|-------------|
| `user_id` | str | Authenticated user's ID |
| `account_tier` | str | free, starter, pro, enterprise |
| `language` | str | Preferred language (BCP 47) |
| `session_id` | str | Current session identifier |
