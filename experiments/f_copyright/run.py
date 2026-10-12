"""Quote-by-title probe. Reference texts are not stored. The rule is in items.json."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

from rt.config import ROOT, load_config, make_client, read_jsonl


def main():
    cfg = load_config(ROOT / "experiments" / "a_thinking_span" / "config.json")
    client = make_client(cfg)
    model = cfg["models"]["8b"]["off"]
    spec = json.loads((Path(__file__).parent / "items.json").read_text(encoding="utf-8"))
    out = ROOT / "results" / "raw" / "f" / "8b_copyright.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {r["key"] for r in read_jsonl(out) if not r.get("error")}
    jobs = []
    for group in ("public_domain", "copyrighted"):
        for item in spec[group]:
            key = f"8b:{group}:{item['id']}"
            if key not in done:
                jobs.append((key, group, item, spec["prompt"].format(title=item["title"])))
    print(f"{len(jobs)} calls -> {out}")
    for n, (key, group, item, prompt) in enumerate(jobs, 1):
        rec = {"key": key, "group": group, "id": item["id"], "title": item["title"],
               "model": model, "prompt": prompt, "ts": datetime.now(timezone.utc).isoformat()}
        try:
            out_chat = client.chat(model, [{"role": "user", "content": prompt}],
                                   max_tokens=180, temperature=0.0, seed=0)
            rec["answer"] = out_chat["answer"]
        except Exception as e:
            rec["error"] = str(e)
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        preview = (rec.get("answer") or rec.get("error", "")).replace("\n", " ")[:90]
        print(f"[{n}/{len(jobs)}] {key} {preview!r}")


if __name__ == "__main__":
    main()
