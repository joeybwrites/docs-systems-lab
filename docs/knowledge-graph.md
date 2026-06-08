# Documentation Knowledge Graph

The sample knowledge graph connects documentation objects to concepts, APIs, workflows, and reader questions. It is intentionally small, but the shape is useful for larger documentation systems.

## Node Types

| Type | Example | Purpose |
| --- | --- | --- |
| Concept | `session-lifecycle` | A reusable idea readers must understand |
| Guide | `quickstart-guide` | A task-oriented page |
| API | `create-session-api` | A reference object |
| Troubleshooting | `auth-token-error` | A known failure mode |
| Release Note | `release-0-4-0` | A change announcement |

## Edge Types

| Relationship | Meaning |
| --- | --- |
| `explains` | A page explains a concept |
| `references` | A guide links to a reference object |
| `unblocks` | A troubleshooting page helps resolve a guide failure |
| `changed_by` | A release note changes expected behavior |
| `requires` | A task depends on a concept or API |

## Use Cases

- Identify missing docs coverage for important concepts
- Route reader questions to the right page type
- Find which pages need updates after an API change
- Evaluate whether retrieval tools select useful sources instead of simply returning more content

## Files

The demo graph lives in:

- `examples/knowledge-graph/nodes.json`
- `examples/knowledge-graph/edges.json`

