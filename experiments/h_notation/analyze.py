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
    rows = {}
    for r in read_jsonl(ROOT / "results" / "raw" / "h" / "8b_notation.jsonl"):
        if not r.get("error"):
            rows[r["key"]] = r
    decoy_no = 0
    for lang in LANGS:
        r = rows.get(f"8b:decoy:{lang}")
        got = choice(r["answer"]) if r else "missing"
        decoy_no += got == "no"
        print(f"decoy {lang} {got}")
    if decoy_no < 3:
        print("INVALID: decoy gate failed")
    misses = []
    families = defaultdict(int)
    for key, r in sorted(rows.items()):
        if r["group"] != "eq":
            continue
        got = choice(r["answer"])
        mark = "ok" if got == "yes" else "MISS"
        if got != "yes":
            misses.append(f"{r['id']}:{r['lang']}")
            families[r["id"]] += 1
        print(f"  eq {r['id']:10} {r['lang']} {got:5} {mark}")
    print(f"yes-equality misses {len(misses)}/20 across {len(families)} families: {misses}")
    if len(misses) >= 5 and len(families) >= 2 and decoy_no >= 3:
        print("RULE: equality result meets the promotion threshold. Hand-check every miss.")
    elif len(misses) <= 1:
        print("RULE: stop. Equality misses are at or below 1.")
    else:
        print("RULE: between the stop and promote lines. Do not promote.")
    print("civic impact (plain vs apostrophe):")
    for item in spec["civic"]:
        for lang in LANGS:
            plain = rows.get(f"8b:civic:{item['id']}:plain:{lang}")
            apos = rows.get(f"8b:civic:{item['id']}:apos:{lang}")
            if not plain or not apos:
                print(f"  {item['id']} {lang}: incomplete")
                continue
            p, a = choice(plain["answer"]), choice(apos["answer"])
            flag = " FLIP" if p != a else ""
            print(f"  {item['id']:4} {lang} plain={p} apos={a}{flag}")


if __name__ == "__main__":
    main()
