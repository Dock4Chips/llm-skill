# Platforms

## Current Support

- `github`: implemented

## Planned Slots

- `producthunt`
- `hackernews`
- `reddit`
- `x`
- `youtube`
- `bilibili`

## Collector Contract

Each platform collector should:

1. Expose a single `collect(output_dir: str | None, use_timestamp: bool)` function.
2. Return a `PlatformReport`.
3. Reuse the shared Markdown renderer unless the platform truly needs a different format.
4. Keep platform-specific scraping logic isolated to its own module.

## File Placement

- Add new collectors under `scripts/collectors/<platform>.py`.
- Keep shared types in `scripts/core/`.
- Register the platform in `scripts/run.py`.
