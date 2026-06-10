# Agent-Readable Docs: llms.txt For The Demo Corpus

Documentation increasingly has two audiences: human readers and AI agents that retrieve, summarize, and answer questions on a reader's behalf. This part of the lab makes the synthetic Atlas SDK corpus agent-readable and keeps that property enforced rather than aspirational.

## What Ships Here

- `examples/product-docs/llms.txt`: a curated markdown index of the corpus following the llms.txt convention (llmstxt.org): one H1 project name, a blockquote summary, and one link-plus-description line per page.
- `tools/agent-readability/`: a TypeScript tool (zero runtime dependencies, Node 20+) that generates the index from corpus structure and validates it so the index cannot silently drift from the docs it describes.

## Why An Index Instead Of More Context

An agent that ingests a whole docs site pays for that choice on every question: more tokens, more latency, more irrelevant context competing with the right answer. The llms.txt pattern is the routing-first alternative: give the agent a small, curated map, let it select the one page that answers the question, and load only that.

This is the same cost-aware position as the rest of the lab: more context is not automatically better, and retrieval should be measured, not assumed.

## Generation Is Derived, Validation Is The Contract

The index is generated from corpus structure (page title, first paragraph) rather than written by hand, so descriptions stay anchored to what pages actually say. Validation is the part that matters operationally. It checks:

- Structure: exactly one H1, a blockquote summary, at least one section of links.
- Referential integrity: every linked file exists; every corpus page is listed.
- Description quality: no empty descriptions.
- Public safety: the same banned-term denylist the Python quality gate enforces.

A docs corpus changes weekly; an unvalidated index is stale the first week nobody remembers to update it. Wiring the validator into CI turns "we have an llms.txt" from a claim into a property.

## Run It

```bash
cd tools/agent-readability
npm install
npm test
npm run validate
```

`npm run gen` regenerates `examples/product-docs/llms.txt` from the corpus.

## Limits

This is a demonstration on a four-page synthetic corpus, and it is built to be read as one.

- The corpus is tiny and regular. The parser's structural assumptions (one H1, first-paragraph summaries) hold here by construction; a real site needs a real markdown pipeline and front-matter conventions.
- No retrieval improvement is measured yet. This slice ships the artifact and its enforcement. Whether routing through this index actually beats loading the full corpus, and by how much at what context cost, is an empirical question the lab's evaluation harness is shaped to answer.
- llms.txt is a convention, not a standard with guaranteed agent uptake. The durable idea is smaller than the file name: publish a curated, validated, machine-readable map of your docs, and keep it true mechanically.
