# AGENTS.md

Operational facts an agent cannot discover by listing files. Kept deliberately minimal: the field evidence (arXiv 2601.20404) says context files pay for themselves only when they are small, non-obvious, and true. CI lints this file with `scripts/agentsmd_lint.py --strict`.

- Everything under `examples/product-docs/` is a synthetic SDK corpus. Never "correct" it against a real product, and never add real product names, internal URLs, or employer references anywhere in this repo. `scripts/quality_gate.py` enforces a banned-term floor; the real boundary is `docs/public-safety.md`.
- Before committing, run `python scripts/quality_gate.py` and `python scripts/token_tax.py --selftest` and `python scripts/agentsmd_lint.py --selftest`. CI runs all three plus the Node tests in `tools/agent-readability/` (`npm test` and `npm run validate` from that directory).
- `examples/product-docs/llms.txt` is generated, not hand-edited. If you change the docs corpus, regenerate it with the tool in `tools/agent-readability/` or CI will fail the drift check.
- `examples/evals/token-tax-results.csv` is a measurement record. Do not regenerate it casually: committed rows are cited by `docs/token-tax.md`, including deliberately retained failure rows.
- Honesty register: every capability claim in `docs/` carries its limits in the same document. Match that register when writing here; this repo's value is the discipline, not the scripts.
