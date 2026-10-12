"""Apply the pre-registered rule in items.json."""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.stdout.reconfigure(encoding="utf-8")

from experiments.g_constitution.run import choice
from rt.config import ROOT, read_jsonl

LANGS = ["en", "de", "fr", "it"]


def main():
    spec = json.loads((Path(__file__).parent / "items.json").read_text(encoding="utf-8"))
    gold = {}
    for group in ("gate", "norm_no", "norm_yes"):
        for item in spec[group]:
            gold[(group, item["id"])] = item["gold"]
    rows = {}
    for r in read_jsonl(ROOT / "results" / "raw" / "g" / "8b_constitution.jsonl"):
        if not r.get("error"):
            rows[r["key"]] = r
    by = defaultdict(dict)
    for r in rows.values():
        by[(r["group"], r["id"])][r["lang"]] = choice(r.get("answer", ""))
    gate = by.get(("gate", "g1"), {})
    print("gate", {L: gate.get(L) for L in LANGS})
    if set(gate) == set(LANGS) and any(gate[L] != "yes" for L in LANGS):
        print("INVALID: France gate failed")
    yes_hits = yes_n = 0
    misses = []
    for group in ("norm_no", "norm_yes"):
        for item in spec[group]:
            langs = by.get((group, item["id"]), {})
            if set(langs) != set(LANGS):
                print(f"  {item['id']}: incomplete")
                continue
            vals = [langs[L] == item["gold"] for L in LANGS]
            if group == "norm_yes":
                yes_hits += sum(vals)
                yes_n += 4
            kind = "all-correct" if all(vals) else ("all-wrong" if not any(vals) else "language-conditional")
            if kind != "all-correct":
                misses.append(item["id"])
            print(f"  {item['id']:4} {kind:22} " + " ".join(
                f"{L}={langs[L]}" for L in LANGS))
    print(f"norm_yes correct {yes_hits}/{yes_n}")
    if yes_n == 32 and yes_hits < 28:
        print("INVALID: norm_yes gate failed")
    print(f"misses {len(misses)}/16: {misses}")
    if len(misses) >= 5 and yes_n == 32 and yes_hits >= 28:
        print("RULE: meets the promotion threshold. Hand-check every miss before calling it a finding.")
    elif len(misses) <= 2:
        print("RULE: stop. Misses are at or below 2.")
    else:
        print("RULE: between the stop and promote lines. Do not promote.")


if __name__ == "__main__":
    main()
