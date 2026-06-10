import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";

import { parsePage } from "../src/corpus.js";
import { generateLlmsTxt, validateLlmsTxt } from "../src/llmstxt.js";

const SAMPLE_PAGE = `# Atlas SDK Quickstart

Atlas SDK is a synthetic example SDK used by this demo. It lets an application create a session.

## Install

\`\`\`bash
# this heading-looking comment must not parse as a heading
npm install @example/atlas-sdk
\`\`\`

## Verify Success

See [Troubleshooting](troubleshooting.md).
`;

test("parsePage extracts title, summary, sections, and links", () => {
  const page = parsePage("quickstart.md", SAMPLE_PAGE);
  assert.equal(page.title, "Atlas SDK Quickstart");
  assert.equal(
    page.summary,
    "Atlas SDK is a synthetic example SDK used by this demo. It lets an application create a session.",
  );
  assert.deepEqual(
    page.sections.map((section) => section.heading),
    ["Install", "Verify Success"],
  );
  assert.deepEqual(page.links, ["troubleshooting.md"]);
});

test("parsePage ignores headings inside code fences", () => {
  const page = parsePage("quickstart.md", SAMPLE_PAGE);
  assert.ok(
    page.sections.every((section) => !section.heading.includes("comment")),
  );
});

function corpusFixture(): { dir: string; pages: ReturnType<typeof parsePage>[] } {
  const dir = mkdtempSync(join(tmpdir(), "agent-readability-"));
  writeFileSync(join(dir, "quickstart.md"), SAMPLE_PAGE, "utf-8");
  return { dir, pages: [parsePage("quickstart.md", SAMPLE_PAGE)] };
}

test("generateLlmsTxt produces a valid file for its own corpus", () => {
  const { dir, pages } = corpusFixture();
  const text = generateLlmsTxt(
    { name: "Atlas SDK Docs", summary: "Synthetic demo docs." },
    pages,
  );
  const result = validateLlmsTxt(text, pages, dir);
  assert.deepEqual(result.failures, []);
  assert.ok(result.ok);
  assert.ok(text.startsWith("# Atlas SDK Docs\n"));
  assert.ok(text.includes("> Synthetic demo docs."));
  assert.ok(
    text.includes(
      "- [Atlas SDK Quickstart](quickstart.md): Atlas SDK is a synthetic example SDK used by this demo.",
    ),
  );
});

test("validateLlmsTxt flags broken links, missing pages, and structure", () => {
  const { dir, pages } = corpusFixture();
  const bad = [
    "# Title",
    "",
    "## Docs",
    "",
    "- [Ghost Page](missing.md): Points nowhere.",
    "",
  ].join("\n");
  const result = validateLlmsTxt(bad, pages, dir);
  assert.equal(result.ok, false);
  assert.ok(result.failures.some((f) => f.includes("missing.md")));
  assert.ok(result.failures.some((f) => f.includes("quickstart.md")));
  assert.ok(result.failures.some((f) => f.includes("blockquote")));
});

test("validateLlmsTxt enforces the public-safety denylist", () => {
  const { dir, pages } = corpusFixture();
  const text = generateLlmsTxt(
    { name: "Atlas SDK Docs", summary: "Synthetic demo docs with a gchat reference." },
    pages,
  );
  const result = validateLlmsTxt(text, pages, dir);
  assert.equal(result.ok, false);
  assert.ok(result.failures.some((f) => f.includes("gchat")));
});
