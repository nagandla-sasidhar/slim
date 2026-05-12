# GhostWriter — AI Content Agent

GhostWriter is an autonomous agent that manages content calendars, drafts blog posts, and publishes to CMS platforms. It is designed for developer-focused content teams who need consistent output without manual overhead.

## What It Does

GhostWriter handles the full content lifecycle:

1. Reads the content calendar from a Notion database or a YAML file
2. Identifies posts that are due within the next seven days
3. Researches each topic by searching the web and reading recent articles
4. Drafts posts in Markdown following the style guide
5. Sends drafts to a Slack channel for review
6. After approval, publishes to Hashnode, Dev.to, or a custom WordPress instance
7. Updates the content calendar to mark the post as published

## Architecture

GhostWriter is built as a Python application using LangGraph for the agent loop. Each stage of the pipeline is a separate node in the graph. This makes it easy to pause at any node, inspect the state, and resume.

The agent state carries the post metadata (title, outline, keywords, target audience) throughout the pipeline. Each node enriches the state and passes it to the next node.

## Installation

GhostWriter requires Python 3.11 or later. Clone the repository and install dependencies:

```bash
git clone https://github.com/your-org/ghostwriter
cd ghostwriter
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

## Configuration

All configuration is in config.yaml. Here are the main sections:

The calendar section defines where GhostWriter reads the content schedule. Set provider to notion or yaml. For Notion, provide the database_id and an integration token. For YAML, provide a path to the schedule file.

The style section defines the voice and format rules. Set tone to one of professional, conversational, or technical. Set target_word_count to the desired length. Set audience to the reader profile.

The publishing section defines where posts go. You can configure multiple destinations and tag them. Each post in the calendar can specify which destinations to publish to.

The review section defines the approval workflow. Set slack_channel to the channel where drafts are posted. Set auto_publish_after_hours to automatically publish if no review feedback arrives within that window. Set to 0 to always require manual approval.

## Style Guide

GhostWriter follows the style configuration in config.yaml, but there are fixed rules it always follows.

Every post starts with a problem statement or a hook. It does not start with "In this post, we will explore."

Code examples are in the appropriate language, are self-contained, and are short. If an example requires more than 30 lines, it links to a full gist or repository instead.

Posts do not use superlatives like "the best," "perfect," or "seamless" unless quoting a real benchmark or a user.

Technical terms are defined on first use. Acronyms are spelled out the first time they appear.

The conclusion summarizes in two sentences and includes one concrete next step for the reader.

## CMS Integration

### Hashnode

Set HASHNODE_API_KEY in your .env file. Set the publication_id in the publishing.hashnode section of config.yaml. GhostWriter creates a draft and sets it to unlisted for review, then publishes on approval.

### Dev.to

Set DEVTO_API_KEY in your .env file. GhostWriter creates a draft article and sends the URL to the review channel. Publishing updates the article to published status.

### WordPress

Set WP_URL, WP_USERNAME, and WP_APP_PASSWORD in your .env file. GhostWriter uses the WordPress REST API. It creates posts as drafts and publishes them after approval.

## Running the Agent

Run a single cycle manually:

```bash
ghostwriter run --once
```

Run continuously on a schedule (reads cron from config):

```bash
ghostwriter run --daemon
```

Dry run to see what would be drafted without writing anything:

```bash
ghostwriter run --dry-run
```

## Reviewing Drafts

When a draft is ready, GhostWriter posts a message in the configured Slack channel. The message includes a link to the draft in Notion or a Google Doc (configurable), the target publication date, and the publishing destinations.

Approve by reacting with a checkmark emoji. Request changes by replying in thread. GhostWriter watches for these signals and acts accordingly.

## Monitoring

GhostWriter logs all actions to logs/ghostwriter.log in JSON format. It exposes a /metrics endpoint on port 9090 in Prometheus format. The key metrics are posts_drafted_total, posts_published_total, and pipeline_duration_seconds.

## Troubleshooting

If a post is stuck in the drafting stage, check the Notion connection and the ANTHROPIC_API_KEY. If publishing fails, check the CMS credentials and the CMS provider's status page. If Slack notifications are not arriving, check the SLACK_BOT_TOKEN and the bot's channel membership.

## Contributing

Contributions are welcome. Please read CONTRIBUTING.md before opening a pull request. Run the test suite with pytest before submitting.
