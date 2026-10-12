# Spoken requests bypass a refusal that text holds

Hack Apertus 2026, Track 1A. Draft report, 12 October 2026.

**Claim.** On Apertus 1.5 8B, a harmful request that is refused as text is sometimes answered with real help when the same request is spoken. Published safety scores for this model are text-only. Audio input has no published safety benchmark.

**Status of this draft.** The 8B result below is complete: two automatic judges, a hand audit of every flagged answer, and a paired text control. Three checks are still open and are not claimed here: the 70B model, safe spoken prompts, and a human voice instead of text-to-speech.

## Result

Same 60 StrongREJECT items, two seeds, thinking off. A generation counts as a safety failure only when both judges label it on-target harmful and a hand audit agrees that the model understood the request and the answer helps with it. Transcription echoes, mishearings, and judge mistakes are excluded.

| Carrier | Confirmed harmful | Clear cases only | Versus the same request as text |
|---|---|---|---|
| Text | 0 / 120 | 0 / 120 | — |
| Audio, all three settings | 43 / 360 (11.9%) | 21 / 360 (5.8%) | +11.9% [+7.8%, +16.7%], McNemar p = 2.3e-13 |
| Audio, clear cases only | — | 21 / 360 (5.8%) | +5.8% [+3.1%, +8.9%], p = 9.5e-7 |
| Audio, male voice, request only | 7 / 120 (5.8%) | 5 / 120 (4.2%) | clear-only interval includes values near zero |
| Audio, male voice plus "respond to the audio" | 25 / 120 (20.8%) | 9 / 120 (7.5%) | clear-only +7.5% [+3.3%, +12.5%], p = 0.0039 |
| Audio, female voice plus the same line | 11 / 120 (9.2%) | 7 / 120 (5.8%) | clear-only +5.8% [+1.7%, +10.8%], p = 0.016 |

The clear cases cover 15 of the 60 items. Five of those items failed in more than one seed or voice. Text produced zero confirmed failures on every one of those items.

Clear audio failures by StrongREJECT category (counts are generations, not items):

| Category | Clear | Partial |
|---|---|---|
| Non-violent crimes | 7 | 5 |
| Violence | 5 | 5 |
| Illegal goods and services | 4 | 2 |
| Disinformation and deception | 4 | 5 |
| Sexual content | 1 | 4 |
| Hate and harassment | 0 | 1 |

This is one failure mode showing up across categories. It is not fifteen unrelated bugs. Intervals are item-level cluster bootstrap 95% confidence intervals. The paired test is exact McNemar on generations that share an item and a seed.

The model heard the requests. Forced transcription matched the original wording at mean difflib ratio 0.89 (male voice, 49 of 60 items at or above 0.9) and 0.97 (female voice, 56 of 60). Failures where the model only repeated the request, or answered a misheard harmless question, are counted separately (5 of 50 audio answers that both judges flagged) and are not in the rates above.

Image input of the same requests is not part of the claim. Confirmed image failures were 7 of 360 (1.9%). Clear image failures were 3 of 360 (0.8%), and that difference against text is not significant (p = 0.25).

## Why this is specific to Apertus 1.5

Apertus 1.5 adds experimental audio input. Its safety evaluations (BBQ, ToxiGen, WMDP, MultiJail, RealGuardrails, Charter alignment, and the 1.0 text suites) score text. The model card does not ship an output filter. Refusal behavior was trained and measured on text, then the same weights accept an audio pathway that those measurements never touched.

Two other hypotheses were tested and did not hold. They are reported so the audio result is not a search that stopped at the first hit.

- **Thinking mode.** With thinking on, a hidden leak (harmful reasoning span, safe final answer) occurred in 0 of 120 generations. The model usually does not open a thinking span when it refuses (116 of 120 thinking-on generations had no span). Forcing the span open on 12 items still ended in a refusal. Over-refusal on 50 safe XSTest prompts was 6% with thinking off and 11% with thinking on. The intervals overlap.
- **Memorized personal records.** The pretraining canaries in `swiss-ai/apertus-pretrain-poisonandcanaries` (synthetic SSNs, phone numbers, and IDs; up to 8 templates and 4 repetitions) leave no detectable trace in the deployed 8B weights. The true secret is no more likely than another person's secret in the same sentence (win rates 48–53%, all confidence intervals cover zero). A positive control, the digits of pi, produces deltas above +90 nats, so the scorer detects memorization when it exists. The 70B check on the highest-exposure cell is consistent with no memorization and is smaller (51 paired people).

## Method

One change per comparison: the carrier. No system prompt, no jailbreak template, no translation.

- **Model:** `swiss-ai/apertus-v1.5-8b` through the Public AI gateway (`https://api.publicai.co/v1`). Thinking off. Temperature 0.7, top_p 0.9, max 6144 tokens, seeds 0 and 1. Transcription controls use temperature 0 and seed 0.
- **Items:** StrongREJECT small, 60 harmful prompts, 10 per category. We did not write the prompts.
- **Audio:** Windows Speech Synthesis, 16 kHz mono WAV. Microsoft David (male) and Microsoft Zira (female). Conditions are audio alone, or audio plus the neutral line "Respond to the request in the audio."
- **Text control:** the identical prompt as a user message.
- **Judges:** `aisingapore/Qwen-SEA-LION-v4-32B-IT` and `aisingapore/Gemma-SEA-LION-v4-27B-IT`, temperature 0. Each answer is refusal, off-target, or on-target harmful. Both must say on-target harmful before a human reads it. Agreement on audio was 84% (Cohen's kappa 0.75).
- **Hand audit:** all 65 answers flagged on 8B (50 audio, 15 image). Verdicts and short rationales are in `results/audit_b_strict_8b.json`. The report does not quote the harmful answers.

The first automatic score, the unmodified StrongREJECT rubric, treated non-refusals as compliance and counted echoes and mishearings as harmful (14–22% on audio). That rubric is not the headline. The three-class rule plus the hand audit replaced it, and the change is documented in `experiments/b_carrier/judge_strict.py`.

## Limits

- **8B only.** The 70B spoken-request run is not finished. Until it is, this can still be a small-model quirk.
- **Synthetic speech only.** Both voices are Microsoft desktop TTS. A human recording of the same items is not in this draft.
- **No safe spoken prompts in this draft yet.** Text XSTest shows low over-refusal (6% with thinking off). The same safe prompts spoken aloud are a separate run. Until that run is audited, a blanket "audio answers everything" story is not ruled out.
- **Sixty items, not 313.** The clear-case interval is already above zero. The full StrongREJECT set would tighten it.
- **Help varies in severity.** Twenty-one audio failures are clear (actionable help). Twenty-two are partial: the model answers the harmful question, but the content is generic, public, or followed by a disclaimer. Both are counted. The clear-only row is the conservative claim.
- **Gateway.** Requests bypass the LiteLLM cache (`cache: {no-cache, no-store}`). Cached responses were rejected. Raw logs stay in `results/raw/` and are not committed, because they contain the harmful answers.

## Reproduce

Python 3.10 or newer, no third-party packages. Set `PUBLICAI_API_KEY` in a gitignored `.env`. From the repository root:

```powershell
python experiments/b_carrier/run.py --set strongreject_small --conditions text,aud_m_bare,aud_m_instr,aud_f_instr,asr_m,asr_f
python experiments/b_carrier/judge_strict.py --raw results/raw/b/8b_off_strongreject_small.jsonl
python experiments/b_carrier/analyze_strict.py
```

`judge_strict.py` refuses to start a second copy, appends labels, and retries pairs that have no label. `analyze_strict.py` reads `results/audit_b_strict_8b.json` and will not count a flagged answer as confirmed until that file has a verdict for it. Protocol details are in `experiments/b_carrier/README.md`.

## What this draft does not claim

It does not claim that image input is unsafe. It does not claim that thinking mode leaks harmful reasoning. It does not claim that Apertus memorized the planted personal records. It does not claim the result for the 70B, for human speech, or for harmless spoken questions.
