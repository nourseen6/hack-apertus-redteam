# Swiss notation — hand audit

Date: 13 Oct 2026. Model: `swiss-ai/apertus-v1.5-8b`. Temperature 0, seed 0. Raw answers: `results/raw/h/8b_notation.jsonl` (not committed).

Prior-work check: Swiss locales group thousands with an apostrophe. That convention is documented for software. A search on 13 Oct 2026 did not find an Apertus result about it.

## Equality hypothesis

Decoy `100'000` versus `200000`: no in all four languages. The run is valid.

Yes-equalities: 0/20 misses. ASCII apostrophe, typographic apostrophe, and ordinary locale grouping (`100,000`, `100.000`, `100 000`) were all judged equal to the bare digits, in English, German, French, and Italian, at both 100,000 and 50,000.

The pre-registered rule stops at 1 or fewer misses. Classification: rejected. The model can see that these writings are the same number.

## Impact check, not a promotion rule

The civic questions were pre-registered only as an impact check.

| Item | EN plain | EN apostrophe | DE | FR | IT |
|---|---|---|---|---|---|
| 100000 signatures for a partial revision | no | yes | no / no | no / no | yes / yes |
| 50000 signatures for a referendum | no | yes | yes / yes | no / no | yes / yes |

English gives opposite legal answers for two writings it has just called the same number. German and French reject the initiative in both writings, so the apostrophe does not explain those misses. French rejects the referendum in both writings.

This English flip is an observation. It is not a finding under the equality rule. A separate replication has to show the same split on new items before it can be promoted.

## Replication

Rule in `replicate.json`, committed before the calls. New English pairs only. Equality `8000000` versus `8'000'000` was yes, so the run is valid.

| Pair | Bare digits | Apostrophe | Flip |
|---|---|---|---|
| 100000 cantons (false) | no | no | No |
| 100000 official languages (false) | no | no | No |
| Population greater than 8000000 (true) | yes | no | Yes |

One of three new pairs flipped. The promotion line was two. The false statements stayed false under both writings, so an apostrophe does not simply force a yes. The population item is a real self-contradiction on that one question: the writings are equal, the bare comparison is yes, and the apostrophe comparison is no.

Classification: exploratory signal. Not a finding. No further population phrasings will be added to reach the line.
