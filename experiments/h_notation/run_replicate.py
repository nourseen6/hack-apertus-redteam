"""Replication for the English notation split. The rule is in replicate.json."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

from experiments.g_constitution.run import choice
from rt.config import ROOT, load_config, make_client, read_jsonl


def main():
    cfg = load_config(ROOT / "experiments" / "a_thinking_span" / "config.json")
    client = make_client(cfg)
    model = cfg["models"]["8b"]["off"]
    spec = json.loads((Path(__file__).parent / "replicate.json").read_text(encoding="utf-8"))
    out = ROOT / "results" / "raw" / "h" / "8b_notation_replicate.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {r["key"] for r in read_jsonl(out) if not r.get("error")}
    jobs = [(f"8b:eq:{spec['equality']['id']}", spec["equality"]["q"], spec["equality"]["gold"], "eq")]
    for pair in spec["pairs"]:
        jobs.append((f"8b:pair:{pair['id']}:plain", pair["plain"], pair["gold_plain"], pair["id"]))
        jobs.append((f"8b:pair:{pair['id']}:apos", pair["apos"], pair["gold_apos"], pair["id"]))
    pending = [j for j in jobs if j[0] not in done]
    print(f"{len(pending)} calls -> {out}")
    for n, (key, question, gold, item_id) in enumerate(pending, 1):
        prompt = question + " " + spec["ask"]
        rec = {"key": key, "id": item_id, "gold": gold, "model": model, "prompt": prompt,
               "ts": datetime.now(timezone.utc).isoformat()}
        try:
            out_chat = client.chat(model, [{"role": "user", "content": prompt}],
                                   max_tokens=16, temperature=0.0, seed=0)
            rec["answer"] = out_chat["answer"]
            rec["choice"] = choice(out_chat["answer"])
        except Exception as e:
            rec["error"] = str(e)
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[{n}/{len(pending)}] {key} {rec.get('choice', 'ERR')} {(rec.get('answer') or '')[:40]!r}")


if __name__ == "__main__":
    main()
