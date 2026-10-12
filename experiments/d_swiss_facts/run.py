"""Swiss factual consistency across EN, DE, FR, IT. Criterion is in items.json."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

from rt.config import ROOT, load_config, make_client, read_jsonl

LANGS = ["en", "de", "fr", "it"]


def norm(text):
    return "".join(ch for ch in (text or "").lower() if ch.isalnum() or ch.isspace()).split()


def matches(answer, gold):
    blob = " ".join(norm(answer))
    for alias in gold:
        a = " ".join(norm(alias))
        if a and (blob == a or blob.startswith(a + " ") or f" {a} " in f" {blob} "):
            return True
    return False


def main():
    cfg = load_config(ROOT / "experiments" / "a_thinking_span" / "config.json")
    client = make_client(cfg)
    model = cfg["models"]["8b"]["off"]
    items = json.loads((Path(__file__).parent / "items.json").read_text(encoding="utf-8"))
    out = ROOT / "results" / "raw" / "d" / "8b_swiss_facts.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {r["key"] for r in read_jsonl(out) if not r.get("error")}
    jobs = []
    for group in ("controls", "swiss"):
        for item in items[group]:
            for lang in LANGS:
                key = f"8b:{group}:{item['id']}:{lang}"
                if key not in done:
                    jobs.append((key, group, item, lang))
    print(f"{len(jobs)} calls -> {out}")
    for n, (key, group, item, lang) in enumerate(jobs, 1):
        rec = {"key": key, "group": group, "id": item["id"], "lang": lang, "model": model,
               "gold": item["gold"], "prompt": item["q"][lang],
               "ts": datetime.now(timezone.utc).isoformat()}
        try:
            out_chat = client.chat(model, [{"role": "user", "content": item["q"][lang]}],
                                   max_tokens=64, temperature=0.0, seed=0)
            rec["answer"] = out_chat["answer"]
            rec["correct"] = matches(out_chat["answer"], item["gold"])
        except Exception as e:
            rec["error"] = str(e)
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        mark = "ERR" if rec.get("error") else ("ok" if rec["correct"] else "MISS")
        print(f"[{n}/{len(jobs)}] {key} {mark} {(rec.get('answer') or '')[:80]!r}")


if __name__ == "__main__":
    main()
