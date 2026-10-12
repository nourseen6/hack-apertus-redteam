# Technical report — Spoken requests bypass text refusals

> Apertus 1.5 8B refuses a harmful request as text and sometimes answers it when the same request is spoken. The comparison holds the prompt fixed, uses two judges plus a hand audit, and excludes mishearings. A 70B refusal drop is measured and is not yet a confirmed harm finding.

**Track:** Apertus Readiness - Track 1A
**Event:** Online
**Team:** Nourseen Tarek
**Demo:** `make replay` prints the committed finding. `make run` runs that check in Docker.

----

### Use of Apertus

- **Model:** swiss-ai/Apertus-v1.5-8B, with a 70B refusal replication in progress
- **How it is used:** red-teaming, inference only
- **Where it runs:** Public AI hosted endpoint, `https://api.publicai.co/v1`

----

## Problem

Published Apertus 1.5 safety scores are text evaluations. Audio input is new in 1.5 and has no published safety benchmark. The question is whether a request the model refuses in text gets real help when the only change is speaking it.

## Red Teaming Method

### Overall Strategy

One change at a time, against a paired control. A rate is a finding only with a denominator, a confidence interval, and a hand audit of every generation that automatic judges flag.

### Discovery Process

Thinking-mode hidden leaks were tested and did not occur (0/120). Memorization of the project's own synthetic personal records was tested and did not occur. Image input of the same harmful requests was too thin to claim (3/360 clear cases, not significant against text). The audio comparison is the result that survived.

### Tooling

Python standard library. Speech is Windows TTS, 16 kHz mono, two voices. Judges are Qwen-SEA-LION 32B and Gemma-SEA-LION 27B. An answer is flagged only when both say it is on-target harmful. A human then labels it a safety failure, an interpretation failure, a factual error, or a judge error. Confirmed rates use safety failures only.

## Findings Dataset

One issue file: `findings/audio_refusal_gap.json`.

On 60 StrongREJECT items, two seeds, thinking off: confirmed harmful help on speech is 43/360 (11.9%) against 0/120 as text. Clear cases only: 21/360 (5.8%), 15 items, paired difference +5.8 points, 95% CI +3.1 to +8.9, McNemar p = 9.5e-7. The model transcribed the audio. Five flagged audio answers were perception or echo failures and are not in the rate.

Self-assessed severity 5, breadth 5. The file states why it is not scored 10.

## Lessons Learnt and Recommendations

Finish the 70B harm audit before calling the issue size-independent. Judge the safe spoken prompts before claiming the model is still helpful on harmless speech. A human recording would answer the synthetic-voice objection. Culture, bias, copyright, and history were not given their own experiments. Empty results on thinking and on planted personal data should stay in the report so the search is visible.

## Reproducibility

`make replay` validates the finding file and prints the summary. It needs Python 3.10+ and no network. `make run` builds `track_1a/Dockerfile` and runs the same check. A live regeneration needs `LLM_API_KEY` and the commands in `experiments/b_carrier/README.md`. Raw model outputs are gitignored because they contain the harmful answers. The finding file contains three paired walkthroughs.

## License

This report is CC BY 4.0. Findings JSON is CDLA-Permissive-2.0. Source code is Apache-2.0.

## References

- Hack Apertus project template, track 1A, https://github.com/HackApertus/project-template
- Apertus-v1.5-8B model card, https://huggingface.co/swiss-ai/Apertus-v1.5-8B
- StrongREJECT, https://github.com/alexandrasouly/strongreject
