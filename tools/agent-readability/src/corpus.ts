/**
 * Markdown corpus loader for the synthetic Atlas SDK docs.
 *
 * Parsing is deliberately structural: title, first-paragraph summary,
 * section headings, relative links, and raw size. No markdown AST
 * dependency is needed for content this regular, and keeping the parser
 * small makes its assumptions easy to audit.
 */

import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

export interface DocSection {
  heading: string;
  level: number;
}

export interface DocPage {
  /** File name relative to the corpus root, e.g. "quickstart.md". */
  file: string;
  title: string;
  /** First body paragraph, joined to a single line. */
  summary: string;
  sections: DocSection[];
  /** Relative markdown link targets found in the page body. */
  links: string[];
  chars: number;
}

const HEADING = /^(#{1,6})\s+(.*)$/;
const MD_LINK = /\[[^\]]*\]\(([^)#\s]+\.md)(?:#[^)]*)?\)/g;

export function parsePage(file: string, text: string): DocPage {
  const lines = text.split(/\r?\n/);
  let title = "";
  const sections: DocSection[] = [];
  const summaryLines: string[] = [];
  let summaryDone = false;
  let inCodeFence = false;

  for (const line of lines) {
    if (line.startsWith("```")) {
      inCodeFence = !inCodeFence;
      continue;
    }
    if (inCodeFence) {
      continue;
    }
    const heading = HEADING.exec(line);
    if (heading !== null) {
      const level = heading[1]?.length ?? 0;
      const text = heading[2]?.trim() ?? "";
      if (level === 1 && title === "") {
        title = text;
      } else {
        sections.push({ heading: text, level });
        summaryDone = true;
      }
      continue;
    }
    if (title !== "" && !summaryDone) {
      if (line.trim() === "") {
        if (summaryLines.length > 0) {
          summaryDone = true;
        }
      } else {
        summaryLines.push(line.trim());
      }
    }
  }

  const links = [...text.matchAll(MD_LINK)].map((match) => match[1] ?? "");

  return {
    file,
    title,
    summary: summaryLines.join(" "),
    sections,
    links,
    chars: text.length,
  };
}

export function loadCorpus(corpusDir: string): DocPage[] {
  return readdirSync(corpusDir)
    .filter((name) => name.endsWith(".md"))
    .sort()
    .map((name) =>
      parsePage(name, readFileSync(join(corpusDir, name), "utf-8")),
    );
}
