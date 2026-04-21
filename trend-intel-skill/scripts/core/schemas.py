from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass
class RawTrendRecord:
    platform: str
    repo_name: str
    repo_url: str
    description: str | None
    language: str | None
    stars_total: int | None
    forks_total: int | None
    stars_period: int | None
    period_label: str | None
    built_by: list[str]
    source_url: str
    crawl_time: str
    parser_version: str = "github-trending-v1"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NormalizedTrendRecord:
    platform: str
    id: str
    title: str
    url: str
    summary: str | None
    category: str | None
    metrics: dict[str, float]
    source: dict[str, str]
    hot_score: float = 0.0
    trend_type: str = "potential"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TrendReport:
    generated_at: str
    platform: str
    window: str
    total: int
    items: list[NormalizedTrendRecord]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["items"] = [item.to_dict() for item in self.items]
        return data

    @classmethod
    def new(cls, platform: str, window: str, items: list[NormalizedTrendRecord]) -> "TrendReport":
        return cls(
            generated_at=datetime.utcnow().isoformat(timespec="seconds") + "Z",
            platform=platform,
            window=window,
            total=len(items),
            items=items,
        )
