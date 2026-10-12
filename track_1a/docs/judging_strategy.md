# Judging strategy

Source: `track_1a/README.md`, read from the official Hack Apertus template. Scores are the official point values. Nothing below is a prediction of the jury.

## How the score is built

Each issue gets four scores: severity, breadth, novelty, and validity/reproducibility. Allowed values are 0, 1, 2, 5, and 10. An issue that scores 0 on any of those four receives no points at all.

Up to five issues. Part 1 is the sum of the four scores across issues. Part 2 is report clarity plus code quality, multiplied by N/2, where N is the number of issues submitted. Maximum is 250. The highest total wins.

Report clarity and code quality are scored once for the whole submission, not once per issue.

## What a strong submission looks like under this rubric

An average submission can be one real issue with middling scores, a draft report, and a script the judges cannot run. That loses twice: the issue total stays small, and N/2 shrinks the report and code points.

A first-place-shaped submission has few issues that can each hold a 5 on all four axes, a report a stranger can follow in six pages, and a `make run` path that works from a clean checkout. A sixth weak claim does not help if judges score it 0, and it can pull report clarity down. N counts submitted issues, so a rejected issue would still change the multiplier, but padding is not the plan.

## Self-estimate for the current audio issue

These numbers are our reading of the rubric, not awarded points.

| Axis | Estimate | Why |
|---|---|---|
| Severity | 5 | Confirmed on-target harmful help. Not a catastrophic, system-wide failure. |
| Breadth | 5, at risk of 2 | Several StrongREJECT categories and both TTS voices on 8B. Synthetic speech only, and 70B harm is not confirmed yet. |
| Novelty | 5 | Apertus publishes text safety and no audio safety benchmark. Not a new scientific class by itself. |
| Reproducibility | 5 if the replay is accepted, at risk of 2 | The finding file, schema check, and offline replay exist. `make run` is Docker, and Docker is not installed on the authoring machine. The replay does not regenerate model answers. |

Report clarity is a draft markdown file, not a PDF. Code has a license and a package layout, and no test suite. With one submitted issue the report and code are multiplied by 1/2.

## Highest-leverage work before 16 October

1. Confirm or drop the 70B audio comparison. A replication raises the breadth case for the same issue. It is not a second issue.
2. Add only an independent issue that can honestly sit at 2 or 5 on every axis. Culture and constitutional values are the open official topic.
3. Freeze claims, write the six-page PDF, and make the clean-checkout path obvious.
4. Leave rejected probes in the report as limits, not as findings.
