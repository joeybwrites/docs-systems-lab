"""Measure the agent token tax of documentation pages.

For each page, compare the size of three things an AI agent could be fed:

1. raw HTML        - what a naive fetch hands the model
2. extracted text  - what a readability-style extraction salvages
3. publisher markdown - the page's .md variant, when the site offers one

The widely repeated claim is that markdown variants cut token cost by ~10x
versus raw HTML. This script measures that ratio on real pages instead of
repeating it. No required dependencies: tiktoken is used for exact token
counts when installed, otherwise a stated chars/4 approximation (ratios are
stable across either method, absolute counts are not).

Usage:
  python scripts/token_tax.py --selftest          offline fixtures, CI-safe
  python scripts/token_tax.py URL [URL ...]       measure specific pages
  python scripts/token_tax.py --sites FILE.json   measure a page list, write CSV
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITES = ROOT / "examples" / "evals" / "token-tax-sites.json"
DEFAULT_OUT = ROOT / "examples" / "evals" / "token-tax-results.csv"

USER_AGENT = "docs-systems-lab-token-tax/0.1 (portfolio measurement; one fetch per variant)"
FETCH_DELAY_SECONDS = 1.0

SKIP_TAGS = {
    "script", "style", "noscript", "svg", "head",
    "nav", "footer", "header", "aside", "template",
}

try:  # exact tokens when available; approximation otherwise
    import tiktoken  # type: ignore

    _ENCODER = tiktoken.get_encoding("cl100k_base")

    def count_tokens(text: str) -> int:
        return len(_ENCODER.encode(text, disallowed_special=()))

    TOKEN_METHOD = "tiktoken/cl100k_base"
except ImportError:  # pragma: no cover - depends on environment
    def count_tokens(text: str) -> int:
        return round(len(text) / 4)

    TOKEN_METHOD = "approx_chars_div_4"


class TextExtractor(HTMLParser):
    """Readability-style extraction: drop chrome and code-adjacent tags, keep prose."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data.strip():
            self._chunks.append(data)

    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self._chunks)).strip()


def extract_text(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    return parser.text()


def fetch(url: str, accept: str = "*/*") -> tuple[int, str] | None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, body
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


def looks_like_markdown(body: str) -> bool:
    head = body.lstrip()[:200].lower()
    return not (head.startswith("<!doctype") or head.startswith("<html"))


def median(values: list[float]) -> float:
    """True median: mean of the two middle elements for even-length lists."""
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return round((ordered[mid - 1] + ordered[mid]) / 2, 1)


def probe_markdown(url: str, html: str) -> tuple[str, str] | None:
    """Try the conventions sites use to expose a markdown variant of a page.

    A response that merely echoes the HTML page (some servers ignore the
    Accept header) is rejected: a markdown variant must differ from the HTML.
    """
    candidates = []
    bare = url.rstrip("/")
    if not bare.endswith(".md"):
        candidates.append(bare + ".md")
        if bare.endswith(".html"):
            candidates.append(bare[: -len(".html")] + ".md")
    for candidate in candidates:
        result = fetch(candidate)
        time.sleep(FETCH_DELAY_SECONDS)
        if result and result[0] == 200 and looks_like_markdown(result[1]) and result[1].strip() != html.strip():
            return candidate, result[1]
    # Content negotiation: some platforms serve markdown for Accept: text/markdown.
    result = fetch(url, accept="text/markdown")
    time.sleep(FETCH_DELAY_SECONDS)
    if result and result[0] == 200 and looks_like_markdown(result[1]) and result[1].strip() != html.strip():
        return url + " (Accept: text/markdown)", result[1]
    return None


def measure_page(url: str) -> dict | None:
    result = fetch(url)
    time.sleep(FETCH_DELAY_SECONDS)
    if not result or result[0] != 200:
        return None
    html = result[1]
    extracted = extract_text(html)
    row = {
        "url": url,
        "html_tokens": count_tokens(html),
        "extracted_tokens": count_tokens(extracted),
        "markdown_tokens": "",
        "markdown_source": "",
        "html_over_extracted": "",
        "html_over_markdown": "",
        "token_method": TOKEN_METHOD,
    }
    if row["extracted_tokens"]:
        row["html_over_extracted"] = round(row["html_tokens"] / row["extracted_tokens"], 1)
    markdown = probe_markdown(url, html)
    if markdown:
        source, body = markdown
        row["markdown_tokens"] = count_tokens(body)
        row["markdown_source"] = source
        if row["markdown_tokens"]:
            row["html_over_markdown"] = round(row["html_tokens"] / row["markdown_tokens"], 1)
    return row


def run(urls: list[str], out_path: Path | None) -> int:
    rows = []
    for url in urls:
        print(f"measuring {url}")
        row = measure_page(url)
        if row is None:
            print("  fetch failed; recorded as unreachable")
            rows.append({"url": url, "html_tokens": "", "extracted_tokens": "",
                         "markdown_tokens": "", "markdown_source": "",
                         "html_over_extracted": "", "html_over_markdown": "",
                         "token_method": TOKEN_METHOD})
            continue
        md = row["markdown_tokens"] or "none"
        print(f"  html={row['html_tokens']}t extracted={row['extracted_tokens']}t "
              f"markdown={md} ratio_html/md={row['html_over_markdown'] or '-'}")
        rows.append(row)
    measured = [r for r in rows if r["html_tokens"] != ""]
    with_md = [r for r in measured if r["markdown_tokens"] != ""]
    print(f"\npages measured: {len(measured)}/{len(rows)}  "
          f"markdown variant found: {len(with_md)}  token method: {TOKEN_METHOD}")
    if with_md:
        ratios = sorted(r["html_over_markdown"] for r in with_md)
        print(f"html/markdown ratio: min {ratios[0]}  median {median(ratios)}  max {ratios[-1]}")
    if measured:
        ratios = sorted(r["html_over_extracted"] for r in measured if r["html_over_extracted"] != "")
        if ratios:
            print(f"html/extracted ratio: min {ratios[0]}  median {median(ratios)}  max {ratios[-1]}")
    if out_path:
        with out_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        try:
            shown = out_path.relative_to(ROOT)
        except ValueError:
            shown = out_path
        print(f"results written to {shown}")
    return 0


FIXTURE_HTML = """<!DOCTYPE html><html><head><title>T</title><style>body{color:red}</style>
<script>var tracking = "lots of javascript an agent never needed";</script></head>
<body><nav>Home Docs API Pricing Blog Careers</nav>
<main><h1>Install the SDK</h1><p>Run the installer, then verify the checksum.</p></main>
<footer>Copyright Legal Privacy Terms Cookies</footer></body></html>"""

FIXTURE_EXPECTED_FRAGMENTS = ["Install the SDK", "verify the checksum"]
FIXTURE_BANNED_FRAGMENTS = ["javascript an agent", "Pricing", "Cookies", "color:red"]


def selftest() -> int:
    failures = []
    extracted = extract_text(FIXTURE_HTML)
    for fragment in FIXTURE_EXPECTED_FRAGMENTS:
        if fragment not in extracted:
            failures.append(f"extraction lost expected content: {fragment!r}")
    for fragment in FIXTURE_BANNED_FRAGMENTS:
        if fragment in extracted:
            failures.append(f"extraction kept chrome/script content: {fragment!r}")
    if not count_tokens(FIXTURE_HTML) > count_tokens(extracted) > 0:
        failures.append("token counts not strictly decreasing from html to extracted")
    if median([1.0, 2.0, 10.0, 11.0]) != 6.0 or median([1.0, 5.0, 9.0]) != 5.0:
        failures.append("median wrong for even- or odd-length input")
    if looks_like_markdown(FIXTURE_HTML):
        failures.append("html fixture misidentified as markdown")
    if not looks_like_markdown("# Install\n\nRun the installer."):
        failures.append("markdown fixture misidentified as html")
    status = "PASS" if not failures else "FAIL"
    print(f"token_tax selftest: {status} ({TOKEN_METHOD})")
    for failure in failures:
        print(f"  {failure}")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="*", help="pages to measure")
    parser.add_argument("--sites", type=Path, help="JSON file with a list of page URLs")
    parser.add_argument("--out", type=Path, help="CSV output path (default with --sites)")
    parser.add_argument("--selftest", action="store_true", help="run offline fixture checks")
    args = parser.parse_args()

    if args.selftest:
        return selftest()
    urls = list(args.urls)
    out_path = args.out
    if args.sites:
        urls.extend(json.loads(args.sites.read_text(encoding="utf-8")))
        out_path = out_path or DEFAULT_OUT
    if not urls:
        parser.error("provide URLs, --sites FILE, or --selftest")
    return run(urls, out_path)


if __name__ == "__main__":
    sys.exit(main())
