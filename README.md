# Docs Systems Lab

Docs Systems Lab is a public-safe portfolio project for demonstrating how documentation teams can move from one-off writing work to repeatable documentation operations.

It uses a synthetic SDK, fake release notes, sample quality manifests, a tiny documentation knowledge graph, and lightweight evaluation scripts to show how docs teams can coordinate AI-assisted authoring, review, retrieval, and publishing without exposing private work.

The project also models a cost-aware AI documentation ethos: use structured state, targeted retrieval, small manifests, and explicit quality gates to get tractable documentation outcomes without relying on long-running, high-token AI sessions for every task.

## What This Demonstrates

- Documentation operating modes for scan, plan, author, review, publish, and learn workflows
- Quality gates that separate drafting speed from publish confidence
- JSON fix manifests for repeatable batch documentation updates
- A small knowledge graph that connects concepts, guides, API references, and troubleshooting pages
- A simple tool-retrieval evaluation that compares selected tools against a random baseline
- Low-overhead AI documentation operations that minimize token spend, review burden, and context drift
- Public/private boundary checks for portfolio-safe documentation systems work

## What This Is Not

This is not a production assistant framework, a live AI agent, or a dump of private operating state. It contains no employer content, internal URLs, private planning files, personal memory, credentials, or unreleased product information.

The purpose is to make documentation systems thinking visible: how a senior documentation engineer structures work so that humans, tooling, and AI assistance can collaborate with less ambiguity.

The emphasis is not "use more AI." The emphasis is designing workflows where AI assistance is bounded, reviewable, and economically tractable.

## Scope and Limits

This is a compact demonstration, not a product. A few things to read honestly:

- `scripts/quality_gate.py` is a structure and public-safety hygiene check (required files, schema, a coarse banned-term scan). It does not judge content quality. Quality as accuracy, clarity, and reader success stays human-owned; the script enforces the mechanical floor only.
- `scripts/eval_tool_retrieval.py` is an illustrative keyword-overlap demo over five hand-written cases. It shows the shape of baseline-relative evaluation. It is not a production metric, is not statistically meaningful, and is not the chance-corrected, information-theoretic method from the related research it gestures at.
- The public-safety term scan is a minimal backstop, not a substitute for human review. A short denylist will miss most real leaks.
- The knowledge graph is a schema sketch, not a system with demonstrated findings.

The value here is the operating model and the discipline, not the size or sophistication of the scripts.

## Quick Start

Run the structure and public-safety checks:

```bash
python scripts/quality_gate.py
```

Run the tool-retrieval evaluation:

```bash
python scripts/eval_tool_retrieval.py
```

Both scripts use only the Python standard library.

## Repo Map

| Path | Purpose |
| --- | --- |
| `docs/operating-modes.md` | Defines the workflow modes a docs team can move through |
| `docs/workflow-gates.md` | Describes gates for source quality, privacy, review, and publishing |
| `docs/knowledge-graph.md` | Explains the sample graph model and why docs teams might use one |
| `docs/evaluation.md` | Documents the retrieval-lift evaluation used by the sample script |
| `docs/public-safety.md` | Defines the public/private boundary for this portfolio repo |
| `examples/product-docs/` | Synthetic SDK docs used as a small docs corpus |
| `examples/manifests/fix-manifest.json` | Sample batch-fix manifest for docs cleanup |
| `examples/knowledge-graph/` | Sample nodes and edges for docs retrieval |
| `examples/evals/tool-retrieval-set.json` | Test cases for retrieval evaluation |
| `scripts/quality_gate.py` | Checks manifest structure, doc hygiene, and public-safety terms |
| `scripts/eval_tool_retrieval.py` | Scores a simple retrieval tool selection task |
| `.github/workflows/quality.yml` | Runs both checks in GitHub Actions |

## Portfolio Framing

This repo is designed to support a portfolio claim like:

> I build documentation systems that connect developer documentation, AI-assisted workflows, quality gates, knowledge graphs, and retrieval evaluation into repeatable, reviewable documentation operations.

Or, more specifically:

> I design low-overhead AI documentation operations that use structured context, targeted retrieval, and quality gates to improve documentation throughput without runaway token cost or review burden.

It is intentionally compact. A reviewer should be able to scan the README, run two scripts, and understand the underlying approach in less than ten minutes.

## Suggested Next Extensions

- Add a static docs site with Docusaurus, Starlight, or VitePress
- Expand the knowledge graph into a browsable visualization
- Add a before/after docs batch-fix example using the manifest
- Add a case study page that maps these patterns to real documentation team workflows without naming private systems

## License

Copyright (c) 2026 Joey Blackwell II. All rights reserved.

This repository is provided as a portfolio sample. You may view the contents for evaluation purposes, but you may not copy, modify, distribute, sublicense, or reuse the work without written permission.
