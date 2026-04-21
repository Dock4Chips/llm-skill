---
name: trend-intel-skill
description: Aggregate and analyze cross-platform trending topics with crawler-based collectors and a shared scoring pipeline. Use when Codex needs to fetch hot trends, rank them by short-term momentum, explain why they are trending, or produce a trend report. Trigger for requests like GitHub trending analysis, weekly trend summaries, hot-topic monitoring, and extensible multi-platform trend collection.
---

# Trend Intel Skill

Use this skill to collect and score trend signals from web pages without API dependencies.

## Run Workflow

1. Select platform collector.
2. Crawl source pages with retries and timeout controls.
3. Normalize records into a shared schema.
4. Compute `hot_score` and trend classification.
5. Return JSON or Markdown report.

## Current Platform

- Implemented collector: `github`.
- Add new platforms by adding a file in `scripts/collectors/` and registering it in `scripts/collectors/__init__.py`.
- Reuse `core/normalize.py` and `core/score.py` without changing interface.

## Command

```bash
python scripts/run.py --platform github --window daily --limit 25 --format markdown
```

## Parameters

- `--platform`: collector name, currently `github`.
- `--window`: `daily|weekly|monthly`.
- `--language`: optional language filter for GitHub Trending URL path.
- `--spoken-language`: optional language code for GitHub Trending query.
- `--limit`: max records.
- `--timeout`: request timeout in seconds.
- `--retries`: retry count.
- `--sleep`: retry backoff base delay.
- `--format`: `json|markdown`.

## Output Rules

- Keep source traceability (`source_url`, `crawl_time`, `parser_version`).
- Sort by `hot_score` descending.
- Include trend category: `breakout|steady|potential`.

## Development Rules

- Keep collector files platform-specific.
- Keep scoring logic platform-agnostic.
- Avoid hard-coding one platform in core modules.
- Update `references/metrics.md` when changing scoring weights or thresholds.
