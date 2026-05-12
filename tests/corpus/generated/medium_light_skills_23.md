Skills
======

This document lists the skills available to the AutoOps agent.

Cloud Operations
----------------

manage_ec2
  Start, stop, or terminate an EC2 instance.
  Inputs: instance_id, action (start|stop|terminate), region
  Requires confirmation: terminate only

manage_rds
  Reboot, stop, or start an RDS instance.
  Inputs: db_identifier, action, region
  Notes: Cannot delete an RDS instance — use the AWS console for deletions

scale_ecs_service
  Update the desired count for an ECS service.
  Inputs: cluster, service, desired_count
  Outputs: updated service ARN and previous count

Observability
-------------

query_cloudwatch
  Run a CloudWatch Insights query over a log group.
  Inputs: log_group, query_string, start_time, end_time
  Outputs: list of result rows

get_metrics
  Retrieve a CloudWatch metric time series.
  Inputs: namespace, metric_name, dimensions, period, stat
  Outputs: list of datapoints

get_alarms
  List CloudWatch alarms in a given state.
  Inputs: state (OK|ALARM|INSUFFICIENT_DATA), prefix
  Outputs: list of alarm names and last state change time

Incident Response
-----------------

page_oncall
  Page the current on-call engineer via PagerDuty.
  Inputs: summary, severity (P1|P2|P3), runbook_url
  Use only for: P1 (production down) and P2 (major degradation)

post_status_page
  Post or update an incident on the status page.
  Inputs: title, status (investigating|identified|monitoring|resolved), message

create_incident_ticket
  Create a Jira incident ticket.
  Inputs: summary, priority, affected_service, description
  Outputs: ticket URL

Automation
----------

run_runbook
  Execute a named runbook from the runbooks/ directory.
  Inputs: runbook_name, params (dict)
  Outputs: execution log

schedule_task
  Schedule a one-off or recurring task.
  Inputs: name, cron_expression, command, notify_on_failure

Usage Notes
-----------

All actions that modify infrastructure are logged to audit-log.json with the requesting user, timestamp, and full input parameters.

Actions marked "Requires confirmation" will show a preview and ask "Proceed? [y/N]" before executing.

Do not chain manage_ec2 terminate with manage_rds actions in the same turn without user review of each step.
