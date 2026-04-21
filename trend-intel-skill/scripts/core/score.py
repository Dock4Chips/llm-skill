from __future__ import annotations

from scripts.core.schemas import NormalizedTrendRecord


def _safe_max(values: list[float]) -> float:
    if not values:
        return 1.0
    max_value = max(values)
    return max_value if max_value > 0 else 1.0


def score_records(records: list[NormalizedTrendRecord]) -> list[NormalizedTrendRecord]:
    stars_period_values = [r.metrics.get("stars_period", 0.0) for r in records]
    stars_total_values = [r.metrics.get("stars_total", 0.0) for r in records]
    forks_total_values = [r.metrics.get("forks_total", 0.0) for r in records]

    max_period = _safe_max(stars_period_values)
    max_total = _safe_max(stars_total_values)
    max_forks = _safe_max(forks_total_values)

    for item in records:
        period_norm = item.metrics.get("stars_period", 0.0) / max_period
        total_norm = item.metrics.get("stars_total", 0.0) / max_total
        forks_norm = item.metrics.get("forks_total", 0.0) / max_forks

        # Weighted toward short-term growth, while keeping baseline popularity and repo utility signals.
        score = (0.55 * period_norm) + (0.25 * forks_norm) + (0.20 * total_norm)
        item.hot_score = round(score * 100, 2)

        if period_norm >= 0.70:
            item.trend_type = "breakout"
        elif period_norm >= 0.35:
            item.trend_type = "steady"
        else:
            item.trend_type = "potential"

    return sorted(records, key=lambda x: x.hot_score, reverse=True)
