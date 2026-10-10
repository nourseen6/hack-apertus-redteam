# Red-Teaming Apertus — Hack Apertus 2026, Track 1A

Research repository for our Track 1A submission to [Hack Apertus 2026](https://hackapertus.devpost.com/).

The goal is not a jailbreak collection, a chatbot, or a generic safety tool. The goal is one real, reproducible failure mode in Apertus 1.5 that its published evaluations could not have caught, backed by controls, rates, and an automated reproduction.

- Submission deadline: **16 October 2026, 12:00 CEST**
- Primary target: `swiss-ai/Apertus-v1.5-8B` (instruct, Charter-aligned)
- Validation target: `swiss-ai/Apertus-v1.5-70B` and the public post-training stage checkpoints

## Status

| Day | Date | Plan | Status |
|---|---|---|---|
| 1 | 8 Oct | Target research, hypotheses, first experiments | Research done |
| 2 | 9–10 Oct | Kill weak hypotheses, pick the strongest real finding | Experiment A harness built; pilot waiting on API key |
| 3–5 | 10–12 Oct | Deep validation, variants, reproducibility | — |
| 6 | 13 Oct | Automated harness, related findings from the same family | — |
| 7 | 14 Oct | Clean end-to-end reproduction | — |
| 8 | 15 Oct | Report, demo, evidence | — |
| 9 | 16 Oct (until 12:00) | Final audit and submission | — |

## What Apertus claims

- **Compliance:** openly available data only, retroactive `robots.txt` opt-out (January 2025), license, toxicity, and PII filtering. No output filter is shipped.
- **Memorization resistance:** Goldfish loss with a 2% mask (`k = 50`) and a 50-token hash window (`h = 50`).
- **Multilingual:** ~1,811 languages in pretraining, Swiss national languages in post-training.
- **Values:** behavior governed by the [Apertus Charter](https://apertus-ai.org/pages/charter/).
- **New in 1.5:** image input, experimental audio input, optional thinking mode with a visible reasoning span, 262,144-token context, tool use.

## What Apertus already tests

- **Memorization:** Gutenberg canary probes on 1.0 base models, greedy and nucleus decoding only. Near-duplicate failures on canonical texts are already published.
- **Text safety:** BBQ, ToxiGen, HarmBench, RealToxicityPrompts, LinguaSafe (1.0); BBQ, ToxiGen, WMDP, MultiJail, PolygloToxicityPrompts, RealGuardrails, Charter Alignment (1.5).
- **Image:** capability, OCR, visual bias, and hallucination benchmarks. No image safety benchmark is published.
- **Audio:** no published benchmark.
- **Thinking mode:** reasoning and math benchmarks only. No safety rows.
- **External:** LatticeFlow (18–21% unguarded attack rejection), Redguard (persona jailbreak), UNICC/EPFL RAG audit.

## Where we are looking

The published evaluations leave three pathways unmeasured:

1. **Thinking mode.** Preference optimization ran with thinking disabled, and no safety score is reported with thinking enabled, but the reasoning span is visible to users.
2. **Modality.** Refusal behavior was trained and measured on text. Image and audio inputs carry the same requests through a different pathway.
3. **Decoder choice for memorization.** Goldfish was measured with greedy and nucleus continuation only. The original Goldfish paper reports that beam search extraction gets easier as `k` grows.

## Top experiments

Each experiment changes one variable against a paired control and is decided by a rate, not by a single output.

### A. Thinking span versus final answer (attack first)

- **Hypothesis:** with `enable_thinking=True`, the reasoning span violates a Charter constraint that the final answer still respects.
- **Control:** the same items with thinking off, plus benign items the model must answer.
- **Measure:** reasoning span and final answer scored separately.
- **Kill condition:** the span refuses whenever the answer refuses, within noise.
- **Scale:** 50 items per behavior class, English plus German, French, and Italian, two seeds.

### B. Same request, different carrier

- **Hypothesis:** a request refused as text is followed when delivered as an image or as speech.
- **Control:** benign image description and audio comprehension must pass first; the text form of each item is the refusal baseline.
- **Kill condition:** refusal rates match across carriers once comprehension controls pass.
- **Scale:** 30 items per carrier, at least two image renderings, crossed with thinking on and off.

### C. Goldfish under a stronger decoder (parallel / fallback)

- **Hypothesis:** beam search or cloze stitching recovers the injected Gutenberg canaries that greedy and nucleus decoding do not.
- **Control:** reproduce the published ~0.18 ROUGE-L baseline first, using [`swiss-ai/apertus-memorization`](https://github.com/swiss-ai/apertus-memorization).
- **Kill condition:** beam and cloze stay within noise of greedy.

## Rejected directions

Generic persona or template jailbreaks, verbatim recall of the canonical texts already listed in the Apertus report, low-resource-language jailbreaks as the main claim, political sycophancy, and "the model hallucinates." Each is either already published or not specific to Apertus.

## Rules for evidence

- No finding from a single output. Every claim needs a paired control, a denominator, and a fixed decoding configuration.
- Record model ID, revision, decoding settings, seed, and the full raw output for every run.
- Before calling anything new, check [`swiss-ai/Apertus-Generation-Issues-Reports`](https://github.com/swiss-ai/Apertus-Generation-Issues-Reports) and the official Getting Started Guide.
- Do not collect or publish personal data about real people. Harmful-content experiments report rates and redacted excerpts only.

## Layout

```
rt/                          shared client (OpenAI-compatible, no dependencies) and dataset loaders
experiments/a_thinking_span/ Experiment A: run, judge, analyze — see its README for the protocol
results/                     summaries (rates only); raw outputs in results/raw/ are git-ignored
report/                      final write-up and figures
```

Requires Python 3.10+ and nothing else.

## Sources

- [Hack Apertus](https://hackapertus.ch/) and [Devpost page](https://hackapertus.devpost.com/)
- [Apertus 1.0 technical report](https://arxiv.org/abs/2509.14233)
- [Apertus 1.5 announcement](https://apertus-ai.org/articles/2026-07-apertus-1-5/)
- [Apertus-v1.5-8B model card](https://huggingface.co/swiss-ai/Apertus-v1.5-8B) and [70B SFT card](https://huggingface.co/swiss-ai/Apertus-v1.5-70B-SFT)
- [Apertus Charter](https://apertus-ai.org/pages/charter/)
- [Goldfish loss paper](https://arxiv.org/abs/2406.10209)
- [LatticeFlow evaluation](https://latticeflow.ai/news/is-swiss-llm-ready-for-enterprise-adoption), [Redguard blog](https://www.redguard.ch/blog/2025/10/09/llm-red-teaming-apertus/), [UNICC/EPFL audit](https://www.unicc.org/wp-content/uploads/2026/07/Safety-Evaluation-of-an-Institutional-LLM-RAG-Deployment-3.pdf)
