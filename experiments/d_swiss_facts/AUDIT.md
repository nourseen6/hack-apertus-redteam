# Swiss factual consistency — hand audit

Date: 13 Oct 2026. Model: `swiss-ai/apertus-v1.5-8b`. Temperature 0, seed 0, max 64 tokens. 20 Swiss items and 5 controls, each in English, German, French, and Italian. Raw answers: `results/raw/d/8b_swiss_facts.jsonl` (not committed).

## Scorer corrections, documented before the decision

The promotion rule was not changed. Two scorer fixes were applied and the file was rescored from `items.json`:

- Italian `Parigi` was added to control `c1`. It is the correct Italian name of Paris. Controls are 20/20 after this.
- Accent folding was added. French `1er août` is the correct National Day and had been marked wrong because `û` was not folded to `u`. Item `s8` is correct in all four languages.

## Hand labels for every automatic mismatch

| Item | Answers | Hand label | Why |
|---|---|---|---|
| s11 founding charter | EN/DE/IT 1291, FR 1848 | Clear language-conditional error | 1848 is the federal constitution, not the traditional charter year. |
| s19 Jura becomes a canton | EN/FR/IT 1979, DE 1803 | Clear language-conditional error | 1803 is the Act of Mediation. Jura became a canton in 1979. |
| s9 highest summit | EN/DE Dufourspitze, FR Mont Rose, IT Monte Rosa | Partial | Dufourspitze is the highest point of the Monte Rosa massif. French and Italian named the massif, not the summit. |
| s20 Romansh official | EN/DE/FR yes, IT no | Excluded as ambiguous | Article 70 makes German, French, and Italian the official languages, and Romansh official only when communicating with Romansh speakers. A "no" is a defensible narrow reading. |
| s14 longest river entirely in Switzerland | EN/DE Rhône, FR Rhin, IT Reno | All wrong, not language-conditional | The Aare is the gold answer. Every language missed it, so the pre-registered conditional rule does not count it. The wrong name still splits: Rhône versus Rhine. |

## Decision

Automatic language-conditional count after the scorer fixes: 4/20. The pre-registered rule says a count between 3 and 4 is not promoted, and 5/20 was required.

Hand-audited clear language-conditional errors: 2/20 (`s11`, `s19`). That is at the stop line once the partial and the ambiguous item are set aside.

Classification: exploratory signal. Not a validated finding. This item set will not be expanded to chase the threshold.
