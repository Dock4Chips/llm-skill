---
name: trend-intel-skill
description: Collect and generate hot/trending intelligence reports from developer platforms. Use when Codex needs to fetch GitHub trending data now, or build/update a reusable cross-platform trend workflow that will later support more sources such as Product Hunt, Hacker News, X, Reddit, YouTube, or other ranking platforms.
---

# Trend Intel Skill

Use the bundled scripts to collect platform trend data and render a Markdown report with a stable structure.

## Workflow

1. Identify the target platform. Use GitHub now. Keep the same output contract for future platforms.
2. Run the platform collector through `scripts/run.py`.
3. Write the report under the requested output directory.
4. Summarize the report path and the key findings for the user.

## Scripts

- `scripts/run.py`: Main entry point. Selects a platform collector and writes the report.
- `scripts/collectors/github.py`: GitHub implementation copied from the project's existing scraper logic, then wrapped for skill usage.
- `scripts/core/schemas.py`: Shared data structures and output contract for every platform.

## Commands

Run GitHub collection:

```bash
python /Users/dock4chips/code_workspace/script-P/llm-skill/trend-intel-skill/scripts/run.py --platform github
```

Run with a custom output directory:

```bash
python /Users/dock4chips/code_workspace/script-P/llm-skill/trend-intel-skill/scripts/run.py --platform github --output-dir /abs/path/to/output
```

Run with timestamped filenames:

```bash
python /Users/dock4chips/code_workspace/script-P/llm-skill/trend-intel-skill/scripts/run.py --platform github --timestamp
```

## Output Contract

- Keep one top-level report per run.
- Keep headings stable so downstream consumers can parse them.
- Keep per-platform collectors returning the same normalized structure.

Read these files only when needed:

- `references/platforms.md`: Supported platform contract and expansion rules.
- `references/output-format.md`: Required Markdown report shape.
- `references/metrics.md`: Meaning of each section and metric.

## Extension Rules

When adding another platform:

1. Add a new collector module under `scripts/collectors/`.
2. Return the shared `PlatformReport` structure from `scripts/core/schemas.py`.
3. Register the collector in `scripts/run.py`.
4. Do not change the GitHub collector unless the GitHub behavior itself needs fixing.
