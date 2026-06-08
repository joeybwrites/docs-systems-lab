# Documentation Operating Modes

Documentation systems work usually fails when every request is treated like a writing task. This demo separates work into operating modes so the right inputs, outputs, and gates are clear at each step.

## Mode Table

| Mode | Primary Question | Inputs | Outputs | Gate |
| --- | --- | --- | --- | --- |
| Scan | What changed? | Release notes, issues, PRs, support signals | Triage notes, candidate doc tasks | Source gate |
| Plan | What should be documented? | Scan output, audience, launch scope | Work plan, owner map, risk list | Scope gate |
| Author | What should the reader see? | Work plan, source material, docs corpus | Draft pages, updates, examples | Style gate |
| Review | Can this ship? | Drafts, manifest, SME feedback | Review verdict, fix list | Quality gate |
| Publish | Is the public state coherent? | Approved docs, changelog, redirects | Published docs, release notes | Publish gate |
| Learn | What should the system remember? | Decisions, review notes, outcomes | Knowledge graph updates, patterns | Memory gate |

## State Contract

A lightweight docs workflow can track state as structured data rather than relying on chat memory.

```json
{
  "workflow": "release-docs",
  "mode": "review",
  "source_state": "verified",
  "privacy_state": "public_safe",
  "open_risks": ["sample-code-still-unverified"],
  "required_gates": ["source", "privacy", "quality"],
  "last_reviewed_by": "docs-reviewer"
}
```

The exact storage layer is less important than the contract. Humans and tools need to agree on what mode the work is in, what evidence has been checked, and what gate remains open.

## Why Modes Matter

Operating modes reduce ambiguity:

- Writers know whether they are exploring, drafting, or publishing.
- Engineers know when a technical review is needed.
- AI tools know whether to summarize, transform, critique, or refuse.
- Reviewers can inspect the same state instead of reconstructing context from chat history.

