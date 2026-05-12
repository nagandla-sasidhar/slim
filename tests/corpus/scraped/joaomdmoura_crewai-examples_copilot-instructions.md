# Copilot Instructions — CrewAI Examples Repository

## Purpose

This repository contains example CrewAI projects demonstrating different agent patterns, crew configurations, and use cases.

## Repository Structure

Each example is a standalone directory:

```
examples/
  trip_planner/           Multi-agent travel planning
  stock_analysis/         Financial research crew
  game_builder_agent/     AI game development crew
  instagram_post/         Content creation pipeline
  landing_page_generator/ Web design crew
  research_crew/          Academic research agents
```

Each example has:
- `README.md` — what the example does and how to run it
- `agents.py` — agent definitions
- `tasks.py` — task definitions
- `crew.py` — crew assembly and kickoff
- `tools/` — custom tools (if any)
- `.env.example` — required environment variables

## Adding a New Example

When adding a new example:

1. Create a directory under `examples/` with a descriptive name (use underscores)
2. Follow the standard file structure above
3. Add a `README.md` explaining:
   - What business problem this crew solves
   - Which agents are involved and their roles
   - How to set up the environment
   - How to run the example
   - Sample output
4. Add the example to the top-level `README.md` table

## Coding Guidelines for Examples

Examples are for learning — prioritize readability over optimization.

- Add comments explaining *why*, not just *what*
- Keep each file under 150 lines — split into modules if longer
- Every tool should have a complete docstring
- Use `os.environ.get("KEY")` for API keys with clear error messages if missing

## Environment Variables

All API keys go in `.env`. Provide an `.env.example` with placeholder values. Never commit real keys.

Typical variables needed:

```
OPENAI_API_KEY=your-key-here
SERPER_API_KEY=your-key-here
```

## Testing Examples

Each example should be testable with:

```bash
cd examples/trip_planner
pip install -r requirements.txt
python crew.py
```

If an example requires paid API credits, note the approximate cost in the README.

## What Copilot Should Know

- CrewAI agents need a `role`, `goal`, and `backstory`
- Tasks need a `description` and `expected_output`
- The `@tool` decorator wraps functions as CrewAI tools
- Use `Process.sequential` for ordered pipelines, `Process.hierarchical` for dynamic delegation
