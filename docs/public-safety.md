# Public-Safety Boundary

This repo is designed for public portfolio use. It should remain synthetic, generic, and inspectable.

## Allowed

- Synthetic product docs
- Generic workflow examples
- Public documentation engineering concepts
- Small local scripts with no network calls
- Sanitized examples of quality gates and manifest-driven updates

## Not Allowed

- Employer content
- Internal URLs or identifiers
- Private planning files
- Personal memory or relationship notes
- Credentials, tokens, or workspace paths
- Unreleased product information
- Claims that imply the demo is a live production system

## Review Checklist

Before publishing or pushing changes:

- Run `python scripts/quality_gate.py`
- Search for private names, URLs, and IDs
- Verify all examples use synthetic product names
- Confirm scripts make no network calls
- Confirm the README describes the project as a demo, not a production system

