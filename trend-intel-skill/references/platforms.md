# Platforms

## GitHub

- Source: `https://github.com/trending`
- Filters:
  - path language: `/trending/<language>`
  - query window: `since=daily|weekly|monthly`
  - query spoken language: `spoken_language_code=<code>`

## Collector Contract

Each collector must return a list of raw records with fields:

- `platform`
- `repo_name`
- `repo_url`
- `description`
- `language`
- `stars_total`
- `forks_total`
- `stars_period`
- `period_label`
- `built_by`
- `source_url`
- `crawl_time`
- `parser_version`

## Extension Rule

When adding platforms, only add a new collector and update collector registry.
Do not fork scoring or output protocols per platform unless strictly required.
