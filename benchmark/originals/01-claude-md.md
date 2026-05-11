# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Structure

```
Practice/
├── content-plan.md                        # LinkedIn post schedule (update status as posts go live)
└── poc/
    └── day-01-openapi-test-generator/     # Day 1 POC — Java 11 Maven multi-agent system
```

## POC: day-01-openapi-test-generator

**What it does:** Multi-agent system that reads a Swagger/OpenAPI spec (URL or file), calls Gemini, and generates a complete BDD (Cucumber + REST Assured) or TDD (TestNG + REST Assured) test suite — controlled by `config.properties`.

### Commands

```bash
cd poc/day-01-openapi-test-generator

# Build
mvn compile

# Run (uses config.properties settings)
mvn compile exec:java

# Build fat JAR
mvn package
java -jar target/openapi-test-generator-1.0-SNAPSHOT.jar
```

### Setup

1. Get a free Gemini API key from https://aistudio.google.com/apikey
2. Open `src/main/resources/config.properties`
3. Set `gemini.api.key`, `swagger.url`, and `test.style`

### Architecture

```
config.properties → Main → AgentConfig → ConfigValidator
                         → OrchestratorAgent
                               → SpecFetcherAgent    (SwaggerFetcherSkill: URL or file)
                               → SpecAnalyzerAgent   (SnakeYAML/Jackson, no LLM)
                               → BDDGeneratorAgent   (4 Gemini calls: feature→stepdefs→pojos→runner)
                                 OR TDDGeneratorAgent (3 Gemini calls: tests→pojos→helper)
                               → FileWriterAgent     (FileWriterSkill)
```

**Package layout:**
- `agents/` — orchestration and workflow steps
- `skills/` — reusable infrastructure (HTTP, file I/O, LLM transport)
- `instructions/` — prompt builders (static methods, no Gemini calls)
- `rules/` — config validation and generation policy
- `config/` — `AgentConfig` loaded from `config.properties`
- `model/` — `SpecSummary`, `GeneratedFile` value objects

**Key design rule:** Step defs are generated AFTER the feature file and receive its content as context — this ensures `@Given/@When/@Then` annotations match the Gherkin steps exactly.

See `docs/ARCHITECTURE.md` for the full guide including how to extend with new test styles or swap the LLM.

### Java Version

Java 11 (LTS). No Java 14+ features — no records, no text blocks, no switch expressions.
