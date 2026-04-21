from __future__ import annotations

import html
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime

from scripts.core.schemas import RawTrendRecord


class GitHubTrendingCollector:
    BASE_URL = "https://github.com/trending"
    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    def collect(
        self,
        *,
        window: str = "daily",
        language: str | None = None,
        spoken_language: str | None = None,
        limit: int = 25,
        timeout: float = 20.0,
        retries: int = 2,
        sleep_seconds: float = 0.8,
    ) -> list[RawTrendRecord]:
        url = self._build_url(window=window, language=language, spoken_language=spoken_language)
        page = self._fetch(url=url, timeout=timeout, retries=retries, sleep_seconds=sleep_seconds)
        crawl_time = datetime.utcnow().isoformat(timespec="seconds") + "Z"

        rows = self._parse_trending_page(page, source_url=url, crawl_time=crawl_time)
        if limit > 0:
            rows = rows[:limit]
        return rows

    def _build_url(self, *, window: str, language: str | None, spoken_language: str | None) -> str:
        path = self.BASE_URL
        if language:
            normalized = language.strip().lower()
            path = f"{self.BASE_URL}/{urllib.parse.quote(normalized)}"

        query: dict[str, str] = {}
        if window in {"daily", "weekly", "monthly"}:
            query["since"] = window
        if spoken_language:
            query["spoken_language_code"] = spoken_language.strip().lower()

        if not query:
            return path
        return path + "?" + urllib.parse.urlencode(query)

    def _fetch(self, *, url: str, timeout: float, retries: int, sleep_seconds: float) -> str:
        err: Exception | None = None

        for attempt in range(retries + 1):
            try:
                req = urllib.request.Request(
                    url=url,
                    headers={
                        "User-Agent": self.USER_AGENT,
                        "Accept": "text/html,application/xhtml+xml",
                        "Accept-Language": "en-US,en;q=0.9",
                    },
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    charset = resp.headers.get_content_charset() or "utf-8"
                    body = resp.read().decode(charset, errors="replace")
                    return body
            except Exception as exc:
                err = exc
                if attempt < retries:
                    time.sleep(sleep_seconds * (attempt + 1))

        raise RuntimeError(f"Failed to fetch GitHub Trending: {err}")

    def _parse_trending_page(self, page: str, *, source_url: str, crawl_time: str) -> list[RawTrendRecord]:
        blocks = re.findall(
            r'<article[^>]*class="[^"]*Box-row[^"]*"[^>]*>(.*?)</article>',
            page,
            flags=re.DOTALL | re.IGNORECASE,
        )

        results: list[RawTrendRecord] = []
        for block in blocks:
            repo_name = self._extract_repo_name(block)
            if not repo_name:
                continue

            repo_url = f"https://github.com/{repo_name}"
            description = self._extract_description(block)
            language = self._extract_language(block)
            stars_total = self._extract_count(block, "/stargazers")
            forks_total = self._extract_count(block, "/forks")
            stars_period, period_label = self._extract_period_stars(block)
            built_by = self._extract_built_by(block)

            results.append(
                RawTrendRecord(
                    platform="github",
                    repo_name=repo_name,
                    repo_url=repo_url,
                    description=description,
                    language=language,
                    stars_total=stars_total,
                    forks_total=forks_total,
                    stars_period=stars_period,
                    period_label=period_label,
                    built_by=built_by,
                    source_url=source_url,
                    crawl_time=crawl_time,
                )
            )

        return results

    def _extract_repo_name(self, block: str) -> str | None:
        hit = re.search(r'href="/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"', block)
        if not hit:
            return None
        return html.unescape(hit.group(1).strip())

    def _extract_description(self, block: str) -> str | None:
        hit = re.search(r"<p[^>]*>(.*?)</p>", block, flags=re.DOTALL | re.IGNORECASE)
        if not hit:
            return None
        return self._strip_tags(hit.group(1))

    def _extract_language(self, block: str) -> str | None:
        hit = re.search(
            r'<span[^>]*itemprop="programmingLanguage"[^>]*>(.*?)</span>',
            block,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if not hit:
            return None
        return self._strip_tags(hit.group(1))

    def _extract_count(self, block: str, marker: str) -> int | None:
        pattern = (
            r'<a[^>]*href="/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+'
            + re.escape(marker)
            + r'"[^>]*>(.*?)</a>'
        )
        hit = re.search(pattern, block, flags=re.DOTALL | re.IGNORECASE)
        if not hit:
            return None
        text = self._strip_tags(hit.group(1)) or ""
        return self._to_int(text)

    def _extract_period_stars(self, block: str) -> tuple[int | None, str | None]:
        hit = re.search(
            r"([0-9][0-9,]*)\s+stars?\s+(today|this week|this month)",
            block,
            flags=re.IGNORECASE,
        )
        if not hit:
            return None, None
        return self._to_int(hit.group(1)), hit.group(2).lower()

    def _extract_built_by(self, block: str) -> list[str]:
        names = re.findall(r'alt="@([A-Za-z0-9_-]+)"', block)
        # Keep original order and remove duplicates.
        seen: set[str] = set()
        unique: list[str] = []
        for name in names:
            if name in seen:
                continue
            seen.add(name)
            unique.append(name)
        return unique

    def _strip_tags(self, chunk: str) -> str | None:
        text = re.sub(r"<[^>]+>", " ", chunk)
        text = html.unescape(re.sub(r"\s+", " ", text)).strip()
        return text or None

    def _to_int(self, value: str) -> int | None:
        digits = re.sub(r"[^0-9]", "", value)
        if not digits:
            return None
        return int(digits)
