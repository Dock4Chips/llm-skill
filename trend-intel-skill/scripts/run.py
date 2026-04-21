from __future__ import annotations

import argparse
import json
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.core.normalize import normalize_records
from scripts.core.schemas import TrendReport
from scripts.core.score import score_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Trend Intel Skill Runner")
    parser.add_argument("--platform", default="github", help="Platform name, e.g. github")
    parser.add_argument("--window", default="daily", choices=["daily", "weekly", "monthly"])
    parser.add_argument("--language", default=None, help="Language filter, e.g. python")
    parser.add_argument("--spoken-language", default=None, help="Spoken language code, e.g. en")
    parser.add_argument("--limit", type=int, default=25, help="Max items to keep")
    parser.add_argument("--timeout", type=float, default=20.0, help="Request timeout seconds")
    parser.add_argument("--retries", type=int, default=2, help="Request retries")
    parser.add_argument("--sleep", type=float, default=0.8, help="Backoff base sleep seconds")
    parser.add_argument("--format", default="json", choices=["json", "markdown"])
    return parser


def format_markdown(report: TrendReport) -> str:
    lines: list[str] = []
    lines.append(f"# {report.platform} trend report ({report.window})")
    lines.append("")
    lines.append(f"generated_at: {report.generated_at}")
    lines.append(f"total: {report.total}")
    lines.append("")

    for idx, item in enumerate(report.items, start=1):
        period = item.metrics.get("stars_period", 0)
        total = item.metrics.get("stars_total", 0)
        forks = item.metrics.get("forks_total", 0)
        lines.append(f"## {idx}. {item.title}")
        lines.append(f"- url: {item.url}")
        if item.summary:
            lines.append(f"- summary: {item.summary}")
        if item.category:
            lines.append(f"- language: {item.category}")
        lines.append(f"- metrics: stars_period={period}, stars_total={total}, forks_total={forks}")
        lines.append(f"- trend_type: {item.trend_type}, hot_score={item.hot_score}")
        lines.append("")

    return "\n".join(lines)


def run() -> int:
    args = build_parser().parse_args()

    collector = get_collector(args.platform)
    raw = collector.collect(
        window=args.window,
        language=args.language,
        spoken_language=args.spoken_language,
        limit=args.limit,
        timeout=args.timeout,
        retries=args.retries,
        sleep_seconds=args.sleep,
    )

    normalized = normalize_records(raw)
    scored = score_records(normalized)
    report = TrendReport.new(platform=args.platform, window=args.window, items=scored)

    if args.format == "markdown":
        print(format_markdown(report))
    else:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
