import argparse
import sys
from pathlib import Path
from typing import Callable, Dict

SKILL_ROOT = Path(__file__).resolve().parents[1]
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))


def _placeholder_collector(platform_name: str) -> Callable:
    def _run(output_dir=None, use_timestamp=False):
        raise NotImplementedError(
            f"Platform '{platform_name}' is reserved but not implemented yet."
        )

    return _run


def _github_collector(output_dir=None, use_timestamp=False):
    from scripts.collectors import github

    return github.collect(output_dir=output_dir, use_timestamp=use_timestamp)


COLLECTORS: Dict[str, Callable] = {
    "github": _github_collector,
    "producthunt": _placeholder_collector("producthunt"),
    "hackernews": _placeholder_collector("hackernews"),
    "reddit": _placeholder_collector("reddit"),
    "x": _placeholder_collector("x"),
    "youtube": _placeholder_collector("youtube"),
    "bilibili": _placeholder_collector("bilibili"),
}


def parse_args():
    parser = argparse.ArgumentParser(description="Run trend-intel-skill collectors.")
    parser.add_argument("--platform", default="github", choices=sorted(COLLECTORS.keys()))
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--timestamp", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    report = COLLECTORS[args.platform](output_dir=args.output_dir, use_timestamp=args.timestamp)
    print(f"platform={report.platform}")
    print(f"date={report.date}")
    print(f"file={report.filename}")


if __name__ == "__main__":
    main()
