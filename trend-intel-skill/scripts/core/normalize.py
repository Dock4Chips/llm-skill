from __future__ import annotations

import re
from typing import Iterable

from .schemas import NormalizedTrendRecord, RawTrendRecord


_whitespace_re = re.compile(r"\s+")


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = _whitespace_re.sub(" ", value).strip()
    return normalized or None


def as_float(value: int | float | None) -> float:
    if value is None:
        return 0.0
    return float(value)


def normalize_records(raw_records: Iterable[RawTrendRecord]) -> list[NormalizedTrendRecord]:
    normalized: list[NormalizedTrendRecord] = []

    for row in raw_records:
        title = clean_text(row.repo_name) or "unknown/unknown"
        normalized.append(
            NormalizedTrendRecord(
                platform=row.platform,
                id=f"{row.platform}:{title}",
                title=title,
                url=row.repo_url,
                summary=clean_text(row.description),
                category=clean_text(row.language),
                metrics={
                    "stars_total": as_float(row.stars_total),
                    "forks_total": as_float(row.forks_total),
                    "stars_period": as_float(row.stars_period),
                    "contributors": float(len(row.built_by)),
                },
                source={
                    "source_url": row.source_url,
                    "crawl_time": row.crawl_time,
                    "parser_version": row.parser_version,
                    "period_label": row.period_label or "unknown",
                },
            )
        )

    return normalized
