"""Constitutional yes/no probe. The decision rule is in items.json."""
import json
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

from rt.config import ROOT, load_config, make_client, read_jsonl

LANGS = ["en", "de", "fr", "it"]
YES = {"yes", "ja", "oui", "si"}
NO = {"no", "nein", "non"}


def fold(text):
    raw = unicodedata.normalize("NFD", text or "")
    raw = "".join(ch for ch in raw if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in raw.lower() if ch.isalnum() or ch.isspace()).split()


def choice(answer):
    words = fold(answer)
    if not words:
        return "blank"
    if words[0] in YES:
        return "yes"
    if words[0] in NO:
        return "no"
    return "other"


def main():
    cfg = load_config(ROOT / "experiments" / "a_thinking_span" / "config.json")
    client = make_client(cfg)
    model = cfg["models"]["8b"]["off"]
    spec = json.loads((Path(__file__).parent / "items.json").read_text(encoding="utf-8"))
    out = ROOT / "results" / "raw" / "g" / "8b_constitution.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {r["key"] for r in read_jsonl(out) if not r.get("error")}
    jobs = []
    for group in ("gate", "norm_no", "norm_yes"):
        for item in spec[group]:
            for lang in LANGS:
                key = f"8b:{group}:{item['id']}:{lang}"
                if key not in done:
                    prompt = item["q"][lang] + " " + spec["ask"][lang]
                    jobs.append((key, group, item, lang, prompt))
    print(f"{len(jobs)} calls -> {out}")
    for n, (key, group, item, lang, prompt) in enumerate(jobs, 1):
        rec = {"key": key, "group": group, "id": item["id"], "lang": lang, "gold": item["gold"],
               "model": model, "prompt": prompt, "ts": datetime.now(timezone.utc).isoformat()}
        try:
            out_chat = client.chat(model, [{"role": "user", "content": prompt}],
                                   max_tokens=16, temperature=0.0, seed=0)
            rec["answer"] = out_chat["answer"]
            rec["choice"] = choice(out_chat["answer"])
            rec["correct"] = rec["choice"] == item["gold"]
        except Exception as e:
            rec["error"] = str(e)
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[{n}/{len(jobs)}] {key} {rec.get('choice', 'ERR')} {(rec.get('answer') or rec.get('error', ''))[:60]!r}")


if __name__ == "__main__":
    main()
