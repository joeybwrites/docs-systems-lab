/**
 * CLI for the agent-readability tool.
 *
 *   node dist/src/cli.js gen        Regenerate llms.txt from the corpus.
 *   node dist/src/cli.js validate   Validate llms.txt against the corpus.
 *
 * Exit code 1 on validation failure so CI can gate on it.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { loadCorpus } from "./corpus.js";
import { generateLlmsTxt, validateLlmsTxt } from "./llmstxt.js";

const TOOL_DIR = dirname(dirname(dirname(fileURLToPath(import.meta.url))));
const REPO_ROOT = dirname(dirname(TOOL_DIR));
const CORPUS_DIR = join(REPO_ROOT, "examples", "product-docs");
const LLMS_TXT_PATH = join(CORPUS_DIR, "llms.txt");

const PROJECT = {
  name: "Atlas SDK Docs",
  summary:
    "Documentation for Atlas SDK, a synthetic example SDK used by Docs Systems Lab to demonstrate documentation operations. Atlas lets an application create a session, send events, and close the session cleanly.",
};

function main(command: string | undefined): number {
  const pages = loadCorpus(CORPUS_DIR);

  switch (command) {
    case "gen": {
      const text = generateLlmsTxt(PROJECT, pages);
      writeFileSync(LLMS_TXT_PATH, text, "utf-8");
      console.log(`Wrote ${LLMS_TXT_PATH} (${pages.length} pages).`);
      return 0;
    }
    case "validate": {
      const text = readFileSync(LLMS_TXT_PATH, "utf-8");
      const result = validateLlmsTxt(text, pages, CORPUS_DIR);
      console.log(
        JSON.stringify(
          {
            status: result.ok ? "passed" : "failed",
            checks: ["structure", "links_resolve", "corpus_coverage", "descriptions", "public_safety"],
            failures: result.failures,
          },
          null,
          2,
        ),
      );
      return result.ok ? 0 : 1;
    }
    default: {
      console.error("Usage: cli.js <gen|validate>");
      return 2;
    }
  }
}

process.exit(main(process.argv[2]));
