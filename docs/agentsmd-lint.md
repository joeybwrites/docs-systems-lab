# Linting Context Files Against the Evidence

AGENTS.md and CLAUDE.md files are the fastest-adopted documentation genre in recent memory, and almost everything written about them is advice. There is now actual evidence: a 2026 field study (Gloaguen et al., arXiv 2601.20404, 138 repositories) measured what context files do to coding-agent performance. Human-written files helped modestly (~+4% task success). LLM-generated files *reduced* success. Every context file added roughly 20% inference cost.

The practical reading: a context file earns its tokens only when it is **small, non-obvious, and true**. `scripts/agentsmd_lint.py` turns that into checks instead of advice.

## Rules

| Rule | Severity | What it catches | Why the evidence cares |
| --- | --- | --- | --- |
| `size` | warning | >150 lines or ~4K tokens | Cost is unconditional; measured value inverts as files grow |
| `tree-dump` | warning | Pasted file trees | An agent discovers structure with one listing; the tree restates the discoverable |
| `readme-duplication` | warning | Lines copied verbatim from README | Discoverable content, paid for twice |
| `script-listing` | note | Blocks restating package.json/Makefile entries | The agent reads the manifest directly |
| `dead-command` | warning | Commands referencing scripts/targets/files that do not exist | A context file that lies is worse than none |
| `vague-imperative` | note | "Write good code," "use best practices" | Uncheckable instructions spend tokens to change nothing |

AGENTS.md is deliberately schema-free, so this is **not** a conformance linter - there is no schema to conform to. It lints against research findings. Where the spec refuses to have an opinion, the evidence has one anyway.

## Usage

```bash
python scripts/agentsmd_lint.py .                 # lint this repo's own AGENTS.md (repo checks on)
python scripts/agentsmd_lint.py --url RAW_URL     # lint any public context file (subset, see Limits)
python scripts/agentsmd_lint.py --selftest        # offline fixtures, CI-safe
python scripts/agentsmd_lint.py . --strict        # exit 1 on warnings - the CI mode
```

This repo dogfoods the rule set: the root `AGENTS.md` was written to pass `--strict`, and CI runs that check on every push - the same generated-must-validate contract the llms.txt tool established.

## Field sample (2026-06-11)

Run against public context files in well-known repos, remote mode:

Six URLs probed; four files found, two 404s.

| File | Result |
| --- | --- |
| openai/codex `AGENTS.md` | warning: 295 lines / ~5.3K tokens, roughly double the evidence-backed budget |
| microsoft/vscode `AGENTS.md` | clean (remote subset) |
| agents.md spec repo's own `AGENTS.md` (both mirrors probed: agentsmd/agents.md and openai/agents.md) | clean (remote subset) |
| 2 other probed repos | no context file at the probed path (404) - itself a datum about adoption unevenness |

## Limits

- **Remote mode runs a subset.** Without the repository, the linter cannot check dead commands, README duplication, or script restating - so "clean" via `--url` is a weaker claim than "clean" against a local repo. The table above says which mode produced each result.
- **The budget numbers are a reading, not a law.** The study did not establish a 150-line threshold; it established that cost is unconditional and benefit is conditional and small. The specific budget here is a defensible operating point, stated so it can be argued with.
- **Heuristics, not judgment.** A vague-imperative regex list catches the cliches it knows. A file can pass every rule and still be useless; the linter enforces the floor the evidence supports, nothing more.
- **Manifests in subdirectories are out of scope.** `dead-command` verifies against the repo root's package.json and Makefile only. Commands qualified as "run from that directory" (including two in this repo's own AGENTS.md, whose package.json lives under `tools/agent-readability/`) are silently skipped, so "lint-clean" is a weaker guarantee for those lines.
- **When both AGENTS.md and CLAUDE.md exist, only AGENTS.md is linted.** Run the tool on each file explicitly to cover both.
- **The sample is six probes, four files.** It demonstrates the tool, not the state of the ecosystem.

## The pair this belongs to

This linter is the *static* half of a question: "is your context file worth its tokens?" The dynamic half - actually measuring agent success on a repo's own tasks with and without its context file, per-repo rather than field-average - is the natural next instrument. The study answered the field-level question; whether *your* file helps *your* repo is still answered by superstition. See also `docs/token-tax.md`: both instruments exist because agent-facing documentation claims circulate faster than data.
