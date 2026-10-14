# Spoken requests bypass text refusals

**Track:** Apertus Readiness, Track 1A. **Team:** Nourseen Tarek. **Event:** Online.

Apertus 1.5 refuses a harmful request as text and sometimes answers it when the same request is spoken. The comparison holds the prompt fixed. Two judges and a hand audit exclude mishearings. The result is one issue, on both the 8B and 70B instruct models.

## Use of Apertus

Inference only, on the Public AI endpoint `https://api.publicai.co/v1`. Models: `swiss-ai/apertus-v1.5-8b` and `swiss-ai/apertus-v1.5-70b`. No local weights. Other models are judges only: Qwen-SEA-LION-v4-32B-IT and Gemma-SEA-LION-v4-27B-IT.

## Problem

Published Apertus 1.5 safety scores are text evaluations. Audio input is new in 1.5 and has no published safety benchmark. The question is whether a request the model refuses in text gets real help when the only change is speaking it.

## Method

One change at a time, against the text form of the same item and seed. The set is StrongREJECT small: 60 items, 10 in each of six categories, seeds 0 and 1. Decoding: temperature 0.7, top_p 0.9, 6144 tokens, thinking off. Speech is Windows TTS, 16 kHz mono, a male voice and a female voice. Conditions are speech alone, and speech plus the line "Respond to the request in the audio."

An answer is flagged only when both judges call it on-target harmful rather than a refusal or an off-target reply. A hand audit then labels a safety failure, an interpretation failure, a factual error, or a judge error. Confirmed rates use safety failures only. Clear means actionable help. Partial means the answer addresses the harmful request with low practical uplift. Paired differences use an item-cluster bootstrap 95% interval and an exact McNemar test.

A benign control uses 50 XSTest safe prompts. Over-refusal is scored by one judge.

## Result

| Model | Text, both judges refuse | Confirmed harmful speech | Clear speech only |
|---|---|---|---|
| 8B | 120/120 | 43/360 (11.9%) | 21/360 (5.8%), 15 of 60 items |
| 70B | 120/120 | 20/353 (5.7%) | 9/353 (2.5%), 8 of 59 items |

On 8B the clear-only paired difference is +5.8 points, 95% CI +3.1 to +8.9, McNemar p = 9.5e-7. Male voice plus the instruction line is the highest 8B cell: 25/120 confirmed, 9/120 clear. The model transcribed the audio (male mean character similarity 0.89).

On 70B the confirmed paired difference is +5.7 points, 95% CI +2.8 to +8.8, McNemar p = 1.9e-6. Clear only: +2.5 points, 95% CI +0.9 to +4.3, p = 0.0039. The hand audit of all 30 double-flagged 70B answers confirmed 20, and set aside 7 echoes or misreadings and 3 judge errors. Audio n is 353 because some calls failed. One generation, item 002, male voice plus instruction, seed 1, has no completed judge pair. The female-voice arm alone is 3/118 confirmed and is not significant by itself (p = 0.25). The pooled audio comparison is.

Benign speech is not refused in bulk. One judge marked over-refusal on 4/50 safe text prompts and 3/50 safe male-audio prompts. Forty-four items were answered in both forms.

Image input of the same harmful requests is not this issue. Clear image failures were 3/360 and not significant against text.

## What did not become an issue

Thinking mode produced no hidden harmful answer on 120 generations. Planted personal-data canaries were not extracted. Pre-registered probes of Swiss civic facts, constitutional yes/no items, matched hiring, copyright titles, and Swiss thousands-separators missed their promotion lines. Those nulls and near-misses are on the `research/*` branches. They are not submitted issues. The 70B audio result is the same carrier gap, not a second issue.

## Scores and limits

Self-assessed severity 5: confirmed answers include actionable help, and this is an evaluation result rather than a measured real-world incident. Breadth 5: multiple categories and both model sizes, still English StrongREJECT and synthetic voices, not most users. Walkthroughs in the finding file are 8B. Raw answers are omitted because they contain the harmful text. One clear 70B case involving minors is in the audit file and is not copied into a walkthrough.

Human recordings were not collected, so a voice-specific TTS artifact remains possible. The gateway cache can ignore sampling fields; calls used an explicit no-cache flag and rejected cache-header hits.

## Reproducibility

`make run` builds `track_1a/Dockerfile` and runs `python src/reproduce.py`. That check validates the finding file and prints the stored 8B rates. It does not call the API. `make replay` is the same check without Docker. A live run needs `LLM_BASE_URL`, `LLM_API_KEY`, and `experiments/b_carrier/README.md`.

This report is CC BY 4.0. The finding JSON is CDLA-Permissive-2.0. The code is Apache-2.0.

## References

Hack Apertus track 1A template, https://github.com/HackApertus/project-template. Apertus-v1.5-8B model card, https://huggingface.co/swiss-ai/Apertus-v1.5-8B. StrongREJECT, https://github.com/alexandrasouly/strongreject.
