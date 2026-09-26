from __future__ import annotations

import random
import re
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from ipaddress import ip_address
from typing import Callable
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


TIMEOUT = 18
MAX_BYTES = 5_000_000
MAX_WORKERS = 3
USER_AGENTS = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
)


@dataclass
class SearchItem:
    rank: int
    title: str
    url: str


@dataclass
class AnalysisResult:
    rank: int
    title: str
    url: str
    headings: str
    estimated_chars: int | None
    status: str

    def to_dict(self) -> dict:
        return asdict(self)


def is_safe_public_url(url: str) -> bool:
    """ローカル・プライベートIPへのアクセスを防ぐ。"""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    try:
        for info in socket.getaddrinfo(parsed.hostname, parsed.port or 443):
            if not ip_address(info[4][0]).is_global:
                return False
    except (socket.gaierror, ValueError):
        return False
    return True


def search_serper(keyword: str, api_key: str) -> list[SearchItem]:
    response = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        json={"q": keyword, "gl": "jp", "hl": "ja", "num": 10},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    organic = response.json().get("organic", [])[:10]
    return [
        SearchItem(index, item.get("title", ""), item.get("link", ""))
        for index, item in enumerate(organic, 1)
        if item.get("link")
    ]


def _extract_page(html: bytes) -> tuple[str, int]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(
        ["script", "style", "noscript", "svg", "nav", "footer", "header", "form"]
    ):
        tag.decompose()

    heading_lines: list[str] = []
    for heading in soup.find_all(["h2", "h3"]):
        text = re.sub(r"\s+", " ", heading.get_text(" ", strip=True))
        if text:
            heading_lines.append(f"{heading.name.upper()}｜{text}")

    main = soup.find("main") or soup.find("article") or soup.body or soup
    visible_text = re.sub(r"\s+", "", main.get_text(" ", strip=True))
    headings = "\n".join(heading_lines) or "見出しを取得できませんでした"
    return headings, len(visible_text)


def analyze_page(item: SearchItem) -> AnalysisResult:
    if not is_safe_public_url(item.url):
        return AnalysisResult(
            item.rank, item.title, item.url, "—", None, "安全上取得できないURL"
        )

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            # 相手サイトへ短時間に集中アクセスしないための小さな待機。
            time.sleep(random.uniform(0.45, 1.15) * (attempt + 1))
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ja-JP,ja;q=0.9,en;q=0.6",
                "Cache-Control": "no-cache",
            }
            with requests.get(
                item.url,
                headers=headers,
                timeout=TIMEOUT,
                stream=True,
                allow_redirects=True,
            ) as response:
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise requests.HTTPError(
                        f"一時的なHTTPエラー {response.status_code}", response=response
                    )
                response.raise_for_status()
                if "text/html" not in response.headers.get("Content-Type", ""):
                    raise ValueError("HTMLページではありません")

                chunks: list[bytes] = []
                size = 0
                for chunk in response.iter_content(64 * 1024):
                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise ValueError("ページ容量が上限を超えました")
                    chunks.append(chunk)

            headings, chars = _extract_page(b"".join(chunks))
            return AnalysisResult(
                item.rank, item.title, item.url, headings, chars, "取得完了"
            )
        except Exception as exc:  # 1サイトの失敗で全体を止めない
            last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (2**attempt))

    return AnalysisResult(
        item.rank,
        item.title,
        item.url,
        "取得できませんでした",
        None,
        str(last_error or "取得エラー")[:100],
    )


def analyze_all(
    items: list[SearchItem],
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[AnalysisResult]:
    results: list[AnalysisResult] = []
    total = len(items)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(analyze_page, item): item for item in items}
        for completed, future in enumerate(as_completed(futures), 1):
            results.append(future.result())
            if progress_callback:
                progress_callback(completed, total)
    return sorted(results, key=lambda result: result.rank)


def demo_results(keyword: str) -> list[AnalysisResult]:
    labels = ["完全ガイド", "初心者向け解説", "専門家が解説", "選び方", "よくある質問"]
    return [
        AnalysisResult(
            index,
            f"{keyword}｜{labels[(index - 1) % len(labels)]}（デモ）",
            f"https://example.com/demo-{index}",
            (
                f"H2｜{keyword}とは\n"
                f"H3｜よくある悩み{index}\n"
                "H2｜選び方とポイント\n"
                "H3｜注意点"
            ),
            3200 + index * 430,
            "デモデータ",
        )
        for index in range(1, 11)
    ]


def research_context(keyword: str, results: list[AnalysisResult], report: str = "") -> str:
    lines = [f"対策キーワード：{keyword}"]
    for result in results:
        lines.append(
            f"\n【{result.rank}位】{result.title}\n"
            f"取得状況：{result.status}\n"
            f"推定文字数：{result.estimated_chars or '不明'}\n"
            f"見出し：\n{result.headings}"
        )
    if report:
        lines.append(f"\n【競合分析レポート】\n{report}")
    return "\n".join(lines)

