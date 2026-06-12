"""Lint an AGENTS.md / CLAUDE.md against the empirical context-file literature.

The 2026 field study of context files (Gloaguen et al., arXiv 2601.20404,
138 repos) found that human-written AGENTS.md files improved agent success
only modestly (~+4%), LLM-generated ones *reduced* success, and every
context file added ~20% inference cost. The practical reading: context
files earn their tokens only when they are small, non-obvious, and true.

This linter turns that reading into checks:

  size                file exceeds the budget where measured value inverts
  tree-dump           file trees the agent can discover with one ls/glob
  readme-duplication  lines copied from README (discoverable content)
  script-listing      blocks restating package.json/Makefile entries
  dead-command        commands referencing scripts/files that do not exist
  vague-imperative    instructions with no checkable content

AGENTS.md is deliberately schema-free, so this is not a conformance check.
It lints against research findings, not against a spec. Standard library
only. Exit code is 0 unless --strict is set and warnings were found.

Usage:
  python scripts/agentsmd_lint.py PATH        file, or repo dir (enables repo checks)
  python scripts/agentsmd_lint.py --url URL   fetch and lint (context-free subset)
  python scripts/agentsmd_lint.py --selftest  offline fixtures, CI-safe
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

LINE_BUDGET = 150
TOKEN_BUDGET = 4000  # approx, chars/4
CONTEXT_FILE_NAMES = ("AGENTS.md", "CLAUDE.md")
TREE_GLYPHS = ("├──", "└──", "│   ")
VAGUE_PATTERNS = [
    r"write (good|clean|high[- ]quality|maintainable) code",
    r"\buse best practices\b",
    r"\bfollow best practices\b",
    r"\bbe (careful|thorough|smart|diligent)\b",
    r"\bensure (high )?quality\b",
    r"\bthink step[- ]by[- ]step\b",
    r"\bdo not (make|introduce) (mistakes|bugs)\b",
]


def approx_tokens(text: str) -> int:
    return round(len(text) / 4)


def find_context_file(path: Path) -> Path | None:
    if path.is_file():
        return path
    for name in CONTEXT_FILE_NAMES:
        candidate = path / name
        if candidate.exists():
            return candidate
    return None


def load_repo_context(repo: Path) -> dict:
    """Collect the discoverable facts the context file should not restate."""
    context: dict = {"readme_lines": set(), "scripts": set(), "make_targets": set()}
    readme = repo / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if len(stripped) >= 40:
                context["readme_lines"].add(stripped)
    package = repo / "package.json"
    if package.exists():
        try:
            data = json.loads(package.read_text(encoding="utf-8", errors="replace"))
            context["scripts"] = set(data.get("scripts", {}))
        except json.JSONDecodeError:
            pass
    makefile = repo / "Makefile"
    if makefile.exists():
        for line in makefile.read_text(encoding="utf-8", errors="replace").splitlines():
            match = re.match(r"^([A-Za-z0-9_.-]+):", line)
            if match:
                context["make_targets"].add(match.group(1))
    return context


COMMAND_PREFIX = r"^(npm|npx|yarn|pnpm|make|python3?|pip3?|node|cargo|go|pytest)\b"


def extract_commands(text: str) -> list[tuple[int, str]]:
    """Commands in inline backticks or fenced code blocks that look like shell invocations."""
    commands = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            candidate = line.strip().lstrip("$ ").strip()
            if re.match(COMMAND_PREFIX, candidate):
                commands.append((number, candidate))
            continue
        for snippet in re.findall(r"`([^`]+)`", line):
            if re.match(COMMAND_PREFIX, snippet.strip()):
                commands.append((number, snippet.strip()))
    return commands


def lint(text: str, repo: Path | None) -> list[dict]:
    findings: list[dict] = []
    lines = text.splitlines()

    if len(lines) > LINE_BUDGET or approx_tokens(text) > TOKEN_BUDGET:
        findings.append({
            "rule": "size", "severity": "warning", "line": 1,
            "detail": f"{len(lines)} lines / ~{approx_tokens(text)} tokens exceeds the "
                      f"budget ({LINE_BUDGET} lines / ~{TOKEN_BUDGET} tokens) past which "
                      f"the field study found context files stop paying for themselves",
        })

    tree_lines = [i for i, line in enumerate(lines, 1) if any(g in line for g in TREE_GLYPHS)]
    if len(tree_lines) >= 3:
        findings.append({
            "rule": "tree-dump", "severity": "warning", "line": tree_lines[0],
            "detail": f"{len(tree_lines)} file-tree lines; agents discover structure "
                      f"with one listing, so the tree spends tokens on the discoverable",
        })

    for number, line in enumerate(lines, 1):
        lowered = line.lower()
        for pattern in VAGUE_PATTERNS:
            if re.search(pattern, lowered):
                findings.append({
                    "rule": "vague-imperative", "severity": "note", "line": number,
                    "detail": f"uncheckable instruction: {line.strip()[:80]!r}",
                })
                break

    if repo is not None:
        context = load_repo_context(repo)
        for number, line in enumerate(lines, 1):
            stripped = line.strip()
            if len(stripped) >= 40 and stripped in context["readme_lines"]:
                findings.append({
                    "rule": "readme-duplication", "severity": "warning", "line": number,
                    "detail": f"line duplicates README.md verbatim: {stripped[:60]!r}",
                })
        known = context["scripts"] | context["make_targets"]
        if known:
            script_mentions = [
                (number, line) for number, line in enumerate(lines, 1)
                if any(f"`npm run {s}`" in line or f"`make {s}`" in line for s in known)
            ]
            for start in range(len(script_mentions) - 2):
                first, _ = script_mentions[start]
                third, _ = script_mentions[start + 2]
                if third - first <= 4:
                    findings.append({
                        "rule": "script-listing", "severity": "note", "line": first,
                        "detail": "3+ nearby lines restate package/Makefile entries an "
                                  "agent reads directly from the manifest",
                    })
                    break
        for number, command in extract_commands(text):
            run_match = re.match(r"^(?:npm|yarn|pnpm) run (\S+)", command)
            make_match = re.match(r"^make (\S+)", command)
            file_match = re.match(r"^(?:python3?|node) (\S+\.(?:py|js|mjs|ts))\b", command)
            if run_match and context["scripts"] and run_match.group(1) not in context["scripts"]:
                findings.append({
                    "rule": "dead-command", "severity": "warning", "line": number,
                    "detail": f"`{command}` references a script not in package.json",
                })
            elif make_match and context["make_targets"] and make_match.group(1) not in context["make_targets"]:
                findings.append({
                    "rule": "dead-command", "severity": "warning", "line": number,
                    "detail": f"`{command}` references a target not in the Makefile",
                })
            elif file_match and not (repo / file_match.group(1)).exists():
                findings.append({
                    "rule": "dead-command", "severity": "warning", "line": number,
                    "detail": f"`{command}` references a file that does not exist",
                })
    return findings


def report(findings: list[dict], source: str, as_json: bool) -> None:
    if as_json:
        print(json.dumps({"source": source, "findings": findings}, indent=2))
        return
    warnings = sum(1 for f in findings if f["severity"] == "warning")
    notes = len(findings) - warnings
    print(f"{source}: {warnings} warning(s), {notes} note(s)")
    for finding in findings:
        print(f"  [{finding['severity']}] line {finding['line']} {finding['rule']}: {finding['detail']}")
    if not findings:
        print("  clean: small, non-obvious, checkable")


FIXTURE_README_LINE = "This synthetic corpus exists to demonstrate documentation operations safely."

FIXTURE_BAD = f"""# Agent guide
Write good code and use best practices. Be careful.
{FIXTURE_README_LINE}
## Layout
├── src
│   ├── app.ts
└── tests
## Scripts
- `npm run build` builds
- `npm run lint` lints
- `npm run check` checks

```bash
npm run build-prod
```
""" + "filler line for the size rule padding out the document\n" * 160

FIXTURE_GOOD = """# AGENTS.md
Run `npm run check` before committing; it is required by CI.
The corpus under examples/product-docs is synthetic; never add real product names.
"""

FIXTURE_PACKAGE = {"scripts": {"check": "node check.js", "build": "node b.js", "lint": "node l.js"}}


def selftest() -> int:
    import tempfile
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "package.json").write_text(json.dumps(FIXTURE_PACKAGE), encoding="utf-8")
        (repo / "README.md").write_text(FIXTURE_README_LINE + "\n", encoding="utf-8")
        bad = lint(FIXTURE_BAD, repo)
        bad_rules = {f["rule"] for f in bad}
        for expected in ("size", "tree-dump", "vague-imperative", "dead-command",
                         "readme-duplication", "script-listing"):
            if expected not in bad_rules:
                failures.append(f"bad fixture should trigger {expected}, got {sorted(bad_rules)}")
        good = lint(FIXTURE_GOOD, repo)
        if good:
            failures.append(f"good fixture should be clean, got {[f['rule'] for f in good]}")
    status = "PASS" if not failures else "FAIL"
    print(f"agentsmd_lint selftest: {status}")
    for failure in failures:
        print(f"  {failure}")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?",
                        help="repo directory, or a context file (repo checks then use the file's parent directory as root)")
    parser.add_argument("--url", help="fetch a raw context file and lint it (no repo checks)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--strict", action="store_true", help="exit 1 if warnings found")
    parser.add_argument("--selftest", action="store_true", help="run offline fixture checks")
    args = parser.parse_args()

    if args.selftest:
        return selftest()
    if args.url:
        request = urllib.request.Request(args.url, headers={"User-Agent": "docs-systems-lab-agentsmd-lint/0.1"})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                text = response.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as error:
            print(f"{args.url}: fetch failed ({error})")
            return 1
        findings = lint(text, repo=None)
        report(findings, args.url, args.json)
    elif args.path:
        target = Path(args.path)
        context_file = find_context_file(target)
        if context_file is None:
            print(f"{target}: no AGENTS.md or CLAUDE.md found")
            return 1
        repo = target if target.is_dir() else target.parent
        findings = lint(context_file.read_text(encoding="utf-8", errors="replace"), repo)
        report(findings, str(context_file), args.json)
    else:
        parser.error("provide PATH, --url, or --selftest")
    if args.strict and any(f["severity"] == "warning" for f in findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
