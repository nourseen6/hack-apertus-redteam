"""Swiss number-notation probe. The decision rule is in items.json."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

from experiments.g_constitution.run import choice
from rt.config import ROOT, load_config, make_client, read_jsonl

LANGS = ["en", "de", "fr", "it"]


def main():
    cfg = load_config(ROOT / "experiments" / "a_thinking_span" / "config.json")
    client = make_client(cfg)
    model = cfg["models"]["8b"]["off"]
    spec = json.loads((Path(__file__).parent / "items.json").read_text(encoding="utf-8"))
    out = ROOT / "results" / "raw" / "h" / "8b_notation.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {r["key"] for r in read_jsonl(out) if not r.get("error")}
    jobs = []
    for lang in LANGS:
        prompt = spec["same"][lang].format(a=spec["decoy"]["a"], b=spec["decoy"]["b"])
        prompt = prompt + " " + spec["ask"][lang]
        jobs.append((f"8b:decoy:{lang}", "decoy", "decoy", lang, "no", prompt))
        for fam in spec["families"]:
            prompt = spec["same"][lang].format(a=fam["a"], b=fam["b"]) + " " + spec["ask"][lang]
            jobs.append((f"8b:eq:{fam['id']}:{lang}", "eq", fam["id"], lang, "yes", prompt))
        loc = spec["locale"][lang]
        prompt = spec["same"][lang].format(a=loc["a"], b=loc["b"]) + " " + spec["ask"][lang]
        jobs.append((f"8b:eq:{loc['id']}:{lang}", "eq", loc["id"], lang, "yes", prompt))
        for item in spec["civic"]:
            for form in ("plain", "apos"):
                prompt = item[form][lang] + " " + spec["ask"][lang]
                jobs.append((f"8b:civic:{item['id']}:{form}:{lang}", "civic", item["id"], lang,
                             item["gold"], prompt, form))
    pending = [j for j in jobs if j[0] not in done]
    print(f"{len(pending)} calls -> {out}")
    for n, job in enumerate(pending, 1):
        key, group, item_id, lang, gold, prompt = job[:6]
        form = job[6] if len(job) > 6 else ""
        rec = {"key": key, "group": group, "id": item_id, "form": form, "lang": lang,
               "gold": gold, "model": model, "prompt": prompt,
               "ts": datetime.now(timezone.utc).isoformat()}
        try:
            out_chat = client.chat(model, [{"role": "user", "content": prompt}],
                                   max_tokens=16, temperature=0.0, seed=0)
            rec["answer"] = out_chat["answer"]
            rec["choice"] = choice(out_chat["answer"])
            rec["correct"] = rec["choice"] == gold
        except Exception as e:
            rec["error"] = str(e)
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[{n}/{len(pending)}] {key} {rec.get('choice', 'ERR')} {(rec.get('answer') or '')[:40]!r}")


if __name__ == "__main__":
    main()
