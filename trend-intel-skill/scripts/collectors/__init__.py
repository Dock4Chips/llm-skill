from __future__ import annotations

from scripts.collectors.github import GitHubTrendingCollector


def get_collector(platform: str):
    key = platform.lower().strip()
    if key == "github":
        return GitHubTrendingCollector()
    raise ValueError(f"Unsupported platform: {platform}")
