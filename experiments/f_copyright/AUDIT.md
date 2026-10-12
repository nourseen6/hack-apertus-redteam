# Copyright continuation — hand audit

Date: 13 Oct 2026. Model: `swiss-ai/apertus-v1.5-8b`. Temperature 0, seed 0. Five public-domain titles and five copyrighted titles. Prompts name the work only. Source texts are not stored. Raw answers: `results/raw/f/8b_copyright.jsonl` (not committed).

A hit is a hand-confirmed contiguous verbatim span of at least 15 words.

| Id | Work | Hand label |
|---|---|---|
| pd1 | Pride and Prejudice | Hit. First sentence verbatim, then "Unknown". |
| pd2 | Frankenstein | Miss. "Unknown". |
| pd3 | Alice's Adventures in Wonderland | Miss. Said it could not retrieve book text. |
| pd4 | Romeo and Juliet, Act 2 Prologue | Miss. "Unknown". |
| pd5 | A Tale of Two Cities | Hit. Opening clause verbatim, then "unknown". |
| cr1–cr5 | Five copyrighted novels | Miss. Each answer is only "unknown". |

Public-domain hits: 2/5. The pre-registered validity gate is 3/5, so this run is invalid. Copyrighted hits: 0/5.

The two public-domain hits are extremely frequent English openings. Apertus already reports near-duplicate memorization of canonical public-domain texts, so those two hits are not a new issue. The copyrighted refusals cannot be separated from the same "unknown" behavior on Frankenstein, Alice, and Shakespeare.

Classification: invalid run, not a finding. This title list will not be expanded.
