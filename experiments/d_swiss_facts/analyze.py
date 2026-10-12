"""Apply the pre-registered rule in items.json. Do not change the rule after seeing scores."""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.stdout.reconfigure(encoding="utf-8")

from rt.config import ROOT, read_jsonl

LANGS = ["en", "de", "fr", "it"]


def main():
    rows = {}
    for r in read_jsonl(ROOT / "results" / "raw" / "d" / "8b_swiss_facts.jsonl"):
        if not r.get("error"):
            rows[r["key"]] = r
    by = defaultdict(dict)
    for r in rows.values():
        by[(r["group"], r["id"])][r["lang"]] = r["correct"]

    def complete(group):
        return {i: langs for (g, i), langs in by.items() if g == group and set(langs) == set(LANGS)}

    controls, swiss = complete("controls"), complete("swiss")
    c_hits = sum(v for langs in controls.values() for v in langs.values())
    c_n = 4 * len(controls)
    print(f"controls correct {c_hits}/{c_n} on {len(controls)} items")
    if c_n and c_hits < 18 and len(controls) == 5:
        print("INVALID: control gate failed")
    cond = []
    for i, langs in sorted(swiss.items()):
        vals = [langs[L] for L in LANGS]
        kind = "all-correct" if all(vals) else ("all-wrong" if not any(vals) else "language-conditional")
        if kind == "language-conditional":
            cond.append(i)
        print(f"  {i:4} {kind:22} " + " ".join(f"{L}={'Y' if langs[L] else 'N'}" for L in LANGS))
    print(f"language-conditional {len(cond)}/{len(swiss)}: {cond}")
    if len(swiss) == 20:
        if len(cond) >= 5:
            print("RULE: meets the pre-registered promotion threshold. Hand-check every conditional item before calling it a finding.")
        elif len(cond) <= 2:
            print("RULE: stop. Language-conditional count is at or below 2.")
        else:
            print("RULE: between the stop and promote lines. Do not promote.")


if __name__ == "__main__":
    main()
