# Output Format

## JSON

Top-level fields:

- `generated_at`
- `platform`
- `window`
- `total`
- `items[]`

Each item should include:

- `id`, `title`, `url`, `summary`, `category`
- `metrics`
- `source`
- `hot_score`
- `trend_type`

## Markdown

- Title with platform and window
- Metadata block: `generated_at`, `total`
- Ranked sections with metrics and trend type

Always keep numerical values in output to support downstream filtering.
