"""Run lightweight quality gates for the Docs Systems Lab demo."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "examples" / "manifests" / "fix-manifest.json"
SCAN_TARGETS = [
    ROOT / "README.md",
    ROOT / "docs",
    ROOT / "examples",
]
REQUIRED_FILES = [
    "README.md",
    "docs/operating-modes.md",
    "docs/workflow-gates.md",
    "docs/knowledge-graph.md",
    "docs/evaluation.md",
    "docs/public-safety.md",
    "examples/product-docs/quickstart.md",
    "examples/product-docs/api-reference.md",
    "examples/product-docs/release-notes.md",
    "examples/product-docs/troubleshooting.md",
    "examples/manifests/fix-manifest.json",
    "examples/evals/tool-retrieval-set.json",
    "docs/token-tax.md",
    "examples/evals/token-tax-sites.json",
]
REQUIRED_MANIFEST_FIELDS = {
    "id",
    "file",
    "issue_type",
    "severity",
    "problem",
    "proposed_fix",
    "reviewer",
    "status",
}
BANNED_PUBLIC_TERMS = [
    "internalfb",
    "workplace",
    "gchat",
    "fbid",
    "source-repo",
    "task-tracker",
]


def fail(failures: list[str], message: str) -> None:
    failures.append(message)


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for target in SCAN_TARGETS:
        if target.is_file():
            files.append(target)
            continue
        files.extend(
            path
            for path in target.rglob("*")
            if path.suffix in {".md", ".json"} and path.is_file()
        )
    return files


def check_required_files(failures: list[str]) -> None:
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).exists():
            fail(failures, f"Missing required file: {relative}")


def check_public_safety(failures: list[str]) -> None:
    patterns = [
        re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
        for term in BANNED_PUBLIC_TERMS
    ]
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            if pattern.search(text):
                relative = path.relative_to(ROOT)
                fail(failures, f"Public-safety term found in {relative}: {pattern.pattern}")


def check_markdown_headings(failures: list[str]) -> None:
    for path in (ROOT / "examples" / "product-docs").glob("*.md"):
        text = path.read_text(encoding="utf-8").strip()
        if not text.startswith("# "):
            fail(failures, f"Missing top-level heading: {path.relative_to(ROOT)}")
        if "TODO" in text:
            fail(failures, f"TODO marker left in doc: {path.relative_to(ROOT)}")


def check_manifest(failures: list[str]) -> None:
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(failures, f"Manifest JSON is invalid: {error}")
        return

    items = manifest.get("items")
    if not isinstance(items, list) or not items:
        fail(failures, "Manifest must include at least one item.")
        return

    valid_statuses = {"ready-for-review", "accepted", "rejected"}
    valid_severities = {"low", "medium", "high"}

    for item in items:
        missing = REQUIRED_MANIFEST_FIELDS - item.keys()
        if missing:
            fail(failures, f"{item.get('id', 'unknown')} missing fields: {sorted(missing)}")
            continue

        target = ROOT / item["file"]
        if not target.exists():
            fail(failures, f"{item['id']} points to missing file: {item['file']}")
        if item["status"] not in valid_statuses:
            fail(failures, f"{item['id']} has invalid status: {item['status']}")
        if item["severity"] not in valid_severities:
            fail(failures, f"{item['id']} has invalid severity: {item['severity']}")


def main() -> int:
    failures: list[str] = []
    check_required_files(failures)
    check_public_safety(failures)
    check_markdown_headings(failures)
    check_manifest(failures)

    result = {
        "status": "failed" if failures else "passed",
        "checks": [
            "required_files",
            "public_safety",
            "markdown_headings",
            "manifest_schema",
        ],
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

