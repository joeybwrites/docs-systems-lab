# Retrieval Evaluation

This repo includes a small evaluation for tool retrieval. The goal is to test whether a routing system selects a useful documentation tool for a reader question.

The sample metric is called retrieval lift. It compares observed tool selection against a random baseline.

Retrieval lift is also a cost-control signal. If a system can select the right tool or source early, it can avoid sending broad context bundles into an AI workflow and reduce downstream human review.

## Evaluation Shape

Each test case has:

- A reader query
- A set of available tools
- One expected tool
- A lightweight keyword overlap scorer

The script ranks tools by overlap between the query and tool metadata. It then checks whether the expected tool appears in the top result and in the top three results.

## Why Compare Against Random?

A retrieval system can look successful when it returns many tools or documents. Comparing against a random baseline asks a better question:

> Did the system select something useful more often than chance?

That question is especially important for documentation systems because over-retrieval can feel helpful while increasing token spend, reader workload, and reviewer effort.

## Cost-Aware Retrieval

AI-assisted documentation systems should not treat more context as automatically better. More context can improve recall, but it can also make every step more expensive and harder to review.

The low-overhead pattern is:

1. Route the question to the smallest useful tool or source set.
2. Use structured metadata before expanding into full document context.
3. Measure whether retrieval beats chance before trusting it in a workflow.
4. Keep humans reviewing focused outputs instead of large undifferentiated context bundles.

## Run It

```bash
python scripts/eval_tool_retrieval.py
```

The output includes case-level results plus top-1 and top-3 accuracy compared with random selection.

## Limits

This is a toy evaluation, and it is built to be read as one. The cases are hand-written and the tool keywords are authored to match them, so a high score here reflects the test design, not a retrieval method proving itself. The lift reported is observed accuracy minus a uniform-random baseline: a coarse comparison, not a chance-corrected or information-theoretic measure. It does not claim production accuracy, academic novelty, or statistical significance. It exists to demonstrate the shape of evaluation thinking that can be expanded into a larger docs retrieval benchmark.
