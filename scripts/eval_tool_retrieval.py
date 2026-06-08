"""Evaluate a tiny documentation tool-retrieval set."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_PATH = ROOT / "examples" / "evals" / "tool-retrieval-set.json"


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def score_tool(query: str, tool: dict) -> float:
    query_tokens = tokens(query)
    tool_text = " ".join(
        [
            tool["id"].replace("_", " "),
            tool["description"],
            " ".join(tool.get("keywords", [])),
        ]
    )
    tool_tokens = tokens(tool_text)
    if not query_tokens:
        return 0.0
    overlap = query_tokens & tool_tokens
    return len(overlap) / math.sqrt(len(query_tokens))


def rank_tools(query: str, tools: list[dict]) -> list[tuple[str, float]]:
    ranked = [
        (tool["id"], score_tool(query, tool))
        for tool in tools
    ]
    return sorted(ranked, key=lambda item: (-item[1], item[0]))


def main() -> None:
    dataset = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    tools = dataset["tools"]
    cases = dataset["cases"]

    results = []
    top_1_hits = 0
    top_3_hits = 0

    for case in cases:
        ranked = rank_tools(case["query"], tools)
        top_1 = [tool_id for tool_id, _ in ranked[:1]]
        top_3 = [tool_id for tool_id, _ in ranked[:3]]
        expected = case["expected_tool"]
        top_1_hit = expected in top_1
        top_3_hit = expected in top_3
        top_1_hits += int(top_1_hit)
        top_3_hits += int(top_3_hit)
        results.append(
            {
                "id": case["id"],
                "query": case["query"],
                "expected_tool": expected,
                "top_1": top_1,
                "top_3": top_3,
                "top_1_hit": top_1_hit,
                "top_3_hit": top_3_hit,
            }
        )

    case_count = len(cases)
    tool_count = len(tools)
    top_1_accuracy = top_1_hits / case_count
    top_3_accuracy = top_3_hits / case_count
    random_top_1 = 1 / tool_count
    random_top_3 = min(3 / tool_count, 1.0)

    summary = {
        "cases": results,
        "summary": {
            "case_count": case_count,
            "tool_count": tool_count,
            "top_1_accuracy": round(top_1_accuracy, 3),
            "top_1_random_baseline": round(random_top_1, 3),
            "top_1_lift_over_random": round(top_1_accuracy - random_top_1, 3),
            "top_3_accuracy": round(top_3_accuracy, 3),
            "top_3_random_baseline": round(random_top_3, 3),
            "top_3_lift_over_random": round(top_3_accuracy - random_top_3, 3),
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

