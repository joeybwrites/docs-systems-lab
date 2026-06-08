# Workflow Gates

Workflow gates convert "looks good" into explicit checks. They do not replace human judgment. They make human judgment easier to apply consistently.

## Gate Types

| Gate | Checks | Typical Failure |
| --- | --- | --- |
| Source | Source material exists and is current | Draft cites an unverified behavior |
| Scope | The work matches the requested audience and release | Page tries to document unrelated features |
| Privacy | Content is public-safe and contains no private identifiers | Internal URL or private project name appears |
| Quality | Page is accurate, readable, complete, and testable | Guide has steps but no validation outcome |
| Publish | Navigation, links, redirects, and release notes are coherent | New page exists but is not discoverable |
| Memory | Reusable decisions and patterns are captured | Same decision must be rediscovered next launch |

## What Is Automated Here

The gates above describe human-applied judgment. In this repo only a thin slice is automated: `scripts/quality_gate.py` enforces structural checks and a coarse Privacy term scan. Source, Scope, Quality, Publish, and Memory stay human decisions. The point of automating the floor is to spend reviewer attention on judgment instead of bookkeeping, not to claim a script can judge documentation quality.

## Gate Response Shape

```json
{
  "gate": "quality",
  "status": "blocked",
  "blocking_findings": [
    {
      "id": "QG-002",
      "severity": "high",
      "file": "examples/product-docs/quickstart.md",
      "finding": "The setup flow does not tell the reader how to verify success.",
      "recommended_fix": "Add a validation step after initializing the SDK session."
    }
  ],
  "reviewer": "docs-quality-gate"
}
```

## Design Principle

A gate should block only when it can explain the failure in terms the next person can act on. A vague gate becomes another source of ambiguity. A useful gate produces a specific next edit, review, or decision.

