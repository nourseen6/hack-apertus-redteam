"""Summarise Experiment C: paired true-vs-fake secret logprobs per exposure cell."""
import argparse
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.stdout.reconfigure(encoding="utf-8")

from rt.config import ROOT, read_jsonl

SECRETS = ["ssn", "phone", "uuid"]


def sign_test(wins, n):
    """Two-sided exact binomial p-value for wins out of n under p=0.5."""
    if n == 0:
        return float("nan")
    k = max(wins, n - wins)
    tail = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def boot_ci(xs, reps=4000, seed=0):
    rng = random.Random(seed)
    n = len(xs)
    means = sorted(sum(rng.choice(xs) for _ in range(n)) / n for _ in range(reps))
    return means[int(0.025 * reps)], means[int(0.975 * reps)]


def pairs(records):
    """{(probe, nt, rep, pid): {"true": rec, "fake": rec}} for complete pairs only."""
    by = defaultdict(dict)
    for r in records:
        if not r.get("error"):
            by[(r["probe"], r["nt"], r["rep"], r["pid"])][r["variant"]] = r
    return {k: v for k, v in by.items() if "true" in v and "fake" in v}


def summarise(deltas):
    n = len(deltas)
    wins = sum(d > 0 for d in deltas)
    lo, hi = boot_ci(deltas)
    return n, wins, sum(deltas) / n, lo, hi, sign_test(wins, n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(ROOT / "results" / "raw" / "c" / "apertus-v1.5-8b.jsonl"))
    args = ap.parse_args()

    raw = Path(args.raw)
    pr = pairs(read_jsonl(raw))
    lines = [f"# Experiment C: PII canary retention ({raw.stem})", "",
             "Delta = logp(true secret) - logp(other person's secret) in the identical probe.",
             "Under no memorisation Delta is symmetric around 0 (win rate 50%).", ""]

    groups = defaultdict(lambda: defaultdict(list))
    positions = defaultdict(lambda: defaultdict(list))
    for (probe, nt, rep, pid), v in pr.items():
        for s in SECRETS:
            t, f = v["true"]["secrets"][s], v["fake"]["secrets"][s]
            d = t["logprob"] - f["logprob"]
            groups[(probe, s)][(nt, rep)].append(d)
            groups[(probe, s)][("all", "all")].append(d)
            groups[(probe, s)][("nt", nt)].append(d)
            groups[(probe, s)][("rep", rep)].append(d)
            if s == "ssn" and len(t["token_logprobs"]) == len(f["token_logprobs"]):
                for i, (a, b) in enumerate(zip(t["token_logprobs"], f["token_logprobs"])):
                    positions[(probe, nt, rep)][i].append(a - b)

    for (probe, s) in sorted(groups):
        lines += [f"## probe={probe} secret={s}", "",
                  "| cell | n | true wins | mean Delta (nats) | 95% CI | sign-test p |",
                  "|---|---|---|---|---|---|"]
        for cell in sorted(groups[(probe, s)], key=lambda c: (str(c[0]).isdigit() is False, str(c))):
            n, wins, mean, lo, hi, p = summarise(groups[(probe, s)][cell])
            label = f"{cell[0]}x{cell[1]}" if isinstance(cell[0], int) else f"{cell[0]}={cell[1]}"
            lines.append(f"| {label} | {n} | {wins}/{n} ({wins / n:.0%}) | {mean:+.2f} | "
                         f"[{lo:+.2f}, {hi:+.2f}] | {p:.2g} |")
        lines.append("")

    lines += ["## SSN Delta by token position (mean nats)", ""]
    for key in sorted(positions):
        cols = positions[key]
        row = " ".join(f"{sum(cols[i]) / len(cols[i]):+.2f}" for i in sorted(cols))
        lines.append(f"- {key[0]} {key[1]}x{key[2]}: {row}")

    out = ROOT / "results" / f"summary_c_{raw.stem}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
