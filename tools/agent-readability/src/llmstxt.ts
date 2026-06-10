/**
 * llms.txt generation and validation for the demo docs corpus.
 *
 * The llms.txt convention (llmstxt.org) puts a small, curated markdown
 * index at a well-known path so LLM agents can route to the right page
 * without ingesting a whole site. This module generates that index from
 * corpus structure and validates it so the file cannot silently drift
 * from the docs it describes.
 */

import { existsSync } from "node:fs";
import { join } from "node:path";

import type { DocPage } from "./corpus.js";

/**
 * Public-safety terms, mirrored from scripts/quality_gate.py. The two
 * lists must stay in sync until the denylist moves to a shared data file.
 */
const BANNED_PUBLIC_TERMS = [
  "internalfb",
  "workplace",
  "gchat",
  "fbid",
  "source-repo",
  "task-tracker",
];

export interface ProjectInfo {
  name: string;
  summary: string;
}

/** First sentence of a summary, for use as a link description. */
function firstSentence(text: string): string {
  const match = /^(.*?[.!?])\s/.exec(`${text} `);
  return (match?.[1] ?? text).trim();
}

export function generateLlmsTxt(project: ProjectInfo, pages: DocPage[]): string {
  const lines: string[] = [];
  lines.push(`# ${project.name}`);
  lines.push("");
  lines.push(`> ${project.summary}`);
  lines.push("");
  lines.push("## Docs");
  lines.push("");
  for (const page of pages) {
    lines.push(`- [${page.title}](${page.file}): ${firstSentence(page.summary)}`);
  }
  lines.push("");
  return lines.join("\n");
}

export interface ValidationResult {
  ok: boolean;
  failures: string[];
}

/**
 * Validate an llms.txt file against the corpus it claims to describe.
 *
 * Checks structure (one H1, blockquote summary, at least one section of
 * links), referential integrity (every linked file exists, every corpus
 * page is listed), description quality (non-empty), and the public-safety
 * denylist.
 */
export function validateLlmsTxt(
  text: string,
  pages: DocPage[],
  corpusDir: string,
): ValidationResult {
  const failures: string[] = [];
  const lines = text.split(/\r?\n/);

  const h1Count = lines.filter((line) => /^# /.test(line)).length;
  if (h1Count !== 1) {
    failures.push(`Expected exactly one H1 title, found ${h1Count}.`);
  }
  if (!lines.some((line) => /^> \S/.test(line))) {
    failures.push("Missing blockquote project summary ('> ...').");
  }
  if (!lines.some((line) => /^## \S/.test(line))) {
    failures.push("Missing at least one '## Section' of links.");
  }

  const linkLine = /^- \[([^\]]+)\]\(([^)]+)\):\s*(.*)$/;
  const listedFiles = new Set<string>();
  for (const line of lines) {
    if (!line.startsWith("- ")) {
      continue;
    }
    const match = linkLine.exec(line);
    if (match === null) {
      failures.push(`Malformed link line: ${line}`);
      continue;
    }
    const [, , target, description] = match;
    if (target !== undefined) {
      listedFiles.add(target);
      if (!existsSync(join(corpusDir, target))) {
        failures.push(`Link target does not exist in corpus: ${target}`);
      }
    }
    if (description === undefined || description.trim() === "") {
      failures.push(`Empty description for link target: ${target ?? "unknown"}`);
    }
  }

  for (const page of pages) {
    if (!listedFiles.has(page.file)) {
      failures.push(`Corpus page missing from llms.txt: ${page.file}`);
    }
  }

  const lower = text.toLowerCase();
  for (const term of BANNED_PUBLIC_TERMS) {
    if (new RegExp(`\\b${term}\\b`).test(lower)) {
      failures.push(`Public-safety term found: ${term}`);
    }
  }

  return { ok: failures.length === 0, failures };
}
