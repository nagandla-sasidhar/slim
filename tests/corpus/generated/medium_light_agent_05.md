# AGENT.md — DataPipeline Orchestrator

## Overview

This agent manages ETL pipelines. It reads from source databases, transforms data according to business rules, and loads results into a data warehouse. It operates in a scheduled batch mode or on-demand trigger mode.

## Responsibilities

- Monitor pipeline health and report failures
- Restart failed pipeline stages automatically
- Send alerts when data quality checks fail
- Generate daily summary reports

## Tools Available

- database_query: Run read-only SQL against configured sources
- pipeline_trigger: Start or restart a named pipeline
- alert_send: Post a message to the configured Slack channel
- report_generate: Produce a PDF or CSV summary from a query result

## Decision Rules

When a pipeline fails:
1. Check the error log for the root cause
2. If the error is transient (timeout, connection reset), retry once after 60 seconds
3. If the error is persistent, send an alert and halt
4. Log all retry attempts

When a data quality check fails:
1. Identify which rows or columns failed
2. Quarantine those records in the staging table
3. Continue processing the valid rows
4. Include a quarantine summary in the daily report

## Permissions

The agent has read access to all source databases listed in config.yml. It has write access only to the staging schema and the reports output directory. It cannot modify schema definitions or drop tables.

## Configuration

Pipeline definitions are in pipelines/. Each YAML file defines source, transformations, destination, and schedule. The agent reads these at startup and reloads them every 10 minutes.

## Monitoring

The agent exposes a /health endpoint on port 8080. It returns 200 if all scheduled pipelines ran within their expected window in the last hour, and 503 otherwise.

## Failure Escalation

If three consecutive pipeline runs fail for the same pipeline, the agent escalates by paging the on-call engineer via PagerDuty. It does not page for single failures.

## Logging

All logs go to stdout in JSON format. Include pipeline_name, stage, timestamp, and error fields in every log line. Use log level INFO for normal operations and ERROR for failures.
