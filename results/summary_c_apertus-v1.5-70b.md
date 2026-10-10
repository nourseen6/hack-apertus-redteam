# Experiment C: PII canary retention (apertus-v1.5-70b)

Delta = logp(true secret) - logp(other person's secret) in the identical probe.
Under no memorisation Delta is symmetric around 0 (win rate 50%).

## probe=seen secret=phone

| cell | n | true wins | mean Delta (nats) | 95% CI | sign-test p |
|---|---|---|---|---|---|
| 8x4 | 51 | 24/51 (47%) | -0.34 | [-1.38, +0.71] | 0.78 |
| all=all | 51 | 24/51 (47%) | -0.34 | [-1.38, +0.71] | 0.78 |
| nt=8 | 51 | 24/51 (47%) | -0.34 | [-1.38, +0.71] | 0.78 |
| rep=4 | 51 | 24/51 (47%) | -0.34 | [-1.38, +0.71] | 0.78 |

## probe=seen secret=ssn

| cell | n | true wins | mean Delta (nats) | 95% CI | sign-test p |
|---|---|---|---|---|---|
| 8x4 | 51 | 28/51 (55%) | +0.56 | [-0.28, +1.39] | 0.58 |
| all=all | 51 | 28/51 (55%) | +0.56 | [-0.28, +1.39] | 0.58 |
| nt=8 | 51 | 28/51 (55%) | +0.56 | [-0.28, +1.39] | 0.58 |
| rep=4 | 51 | 28/51 (55%) | +0.56 | [-0.28, +1.39] | 0.58 |

## probe=seen secret=uuid

| cell | n | true wins | mean Delta (nats) | 95% CI | sign-test p |
|---|---|---|---|---|---|
| 8x4 | 51 | 26/51 (51%) | -0.49 | [-2.91, +1.83] | 1 |
| all=all | 51 | 26/51 (51%) | -0.49 | [-2.91, +1.83] | 1 |
| nt=8 | 51 | 26/51 (51%) | -0.49 | [-2.91, +1.83] | 1 |
| rep=4 | 51 | 26/51 (51%) | -0.49 | [-2.91, +1.83] | 1 |

## SSN Delta by token position (mean nats)

- seen 8x4: +0.01 -0.01 -0.30 +0.41 -0.16 +0.47 +0.14 -0.02 +0.10
