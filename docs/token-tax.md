# The Agent Token Tax

When an AI agent reads a documentation page, what it pays depends on what it is fed. This measurement compares three options across real documentation sites:

1. **Raw HTML** - what a naive fetch hands the model
2. **Extracted text** - what readability-style extraction salvages from that HTML
3. **Publisher markdown** - the `.md` variant of the page, where the site offers one

A widely repeated claim says markdown variants cut token cost roughly 10x versus HTML. The claim circulates without published per-site data. `scripts/token_tax.py` measures it.

## Method

For each page in `examples/evals/token-tax-sites.json`, the script fetches the raw HTML, runs a standard-library readability-style extraction (dropping script, style, noscript, svg, head, nav, header, footer, aside, and template tags), and probes for a markdown variant two ways: the `.md` URL suffix convention (used by several docs platforms), then `Accept: text/markdown` content negotiation. A negotiated response that merely echoes the HTML page is rejected — a markdown variant must differ from the HTML. Token counts use tiktoken (cl100k_base) when installed, otherwise a stated chars/4 approximation. Ratios are stable across either method; absolute counts are not. One fetch per variant, 1-second delays, identified user agent.

Run it:

```bash
python scripts/token_tax.py --sites examples/evals/token-tax-sites.json
python scripts/token_tax.py https://any.docs.site/page        # single pages
python scripts/token_tax.py --selftest                        # offline, CI-safe
```

## Findings (first run, 2026-06-11, 10 pages)

Full data: `examples/evals/token-tax-results.csv`.

| Measure | Result |
| --- | --- |
| Pages with a working markdown variant | 5 of 10 probed, all via the `.md` suffix (one content-negotiation echo was auto-rejected, see Limits) |
| html/markdown token ratio (5 variant pages) | min 18.0x, median 74.7x, max 186.0x |
| html/extracted ratio (all 10 pages) | median 42.9x, but see Limits |
| Largest single page | 512K tokens of HTML for a page whose markdown is 14.5K tokens |

Three observations worth the reader's time:

- **The "10x" claim is understated for modern docs platforms.** On this sample the markdown variant saves 18x to 186x, not 10x. The driver is that contemporary docs sites ship very large script/style/framework payloads: one measured page was 282,991 tokens of HTML for 3,790 tokens of markdown content.
- **Markdown variants are quietly widespread.** GitHub Docs, Stripe Docs, and Mintlify-hosted sites all answer the `.md` suffix. An agent (or tool author) that does not probe for them routinely pays a 20-100x overage. Classic static sites (MDN, docs.python.org, MkDocs/FastAPI) do not offer them - there, extraction is the only relief.
- **Older "heavy" sites are cheaper than new "light" ones.** docs.python.org raw HTML was ~9K tokens - smaller than the *markdown variant* of some modern pages. The token tax is a platform-generation effect, not a content-size effect.

## Limits

Read these before quoting the numbers:

- **Sample size is 10 pages.** This is a first measurement, not a survey. The site list is committed; extending it is one JSON edit.
- **The extractor is deliberately simple.** Standard-library tag filtering, not a production readability algorithm. On JS-rendered pages it salvages little (one page extracted to 117 tokens because content is client-rendered), which inflates html/extracted ratios. Those ratios are a lower bound on extraction quality, not a verdict.
- **Content negotiation found nothing on this sample - and caught a liar.** One site returned an identical body for `Accept: text/markdown`; the initial version of this script accepted it, blind review caught the bogus 1.0x row, and the script now rejects negotiated responses that echo the HTML. All five valid variants came from the `.md` suffix. The bug-to-fix story is left in this paragraph on purpose: instruments improve by being wrong in public.
- **Token counts in the committed run are chars/4 approximations** (tiktoken was not installed for the run). Ratios are robust to this; absolute counts within ~15% are not guaranteed.
- **JS-rendered and bot-gated pages can lie.** One site returned a 1.6K-token shell to this user agent; its row is meaningless and visibly so. Honest instruments show their failures.

## Why this lives here

The lab's llms.txt work (`docs/agent-readability.md`) generates and validates an agent-facing index. This measurement is the other half of the argument: *what it costs an agent when that layer is missing*. Together they make the case that agent-readable documentation is an engineering discipline with measurable stakes, not a fashion.
