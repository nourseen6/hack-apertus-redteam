"""Generate paired thinking-off / thinking-on outputs for an item set.

Output is append-only JSONL; rerunning the same command resumes where it stopped.
"""
import argparse
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.stdout.reconfigure(encoding="utf-8")

from rt.config import ROOT, load_config, make_client, model_spec, read_jsonl
from rt.data import load_set


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(Path(__file__).with_name("config.json")))
    ap.add_argument("--set", required=True, choices=["strongreject_small", "strongreject", "xstest_safe"])
    ap.add_argument("--size", default="8b")
    ap.add_argument("--conditions", default="off,on")
    ap.add_argument("--seeds", default="0,1")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    cfg = load_config(args.config)
    gen = cfg["generation"]
    client = make_client(cfg)
    items = load_set(args.set, limit=args.limit)
    conditions = args.conditions.split(",")
    seeds = [int(s) for s in args.seeds.split(",")]

    out_path = Path(args.out or ROOT / "results" / "raw" / "a" / f"{args.size}_{args.set}.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = {r["key"] for r in read_jsonl(out_path) if not r.get("error")}

    jobs = []
    for item in items:
        for condition in conditions:
            for seed in seeds:
                key = f"{args.size}:{item['id']}:{condition}:{seed}"
                if key not in done:
                    jobs.append((key, item, condition, seed))
    print(f"{len(items)} items, {len(jobs)} generations to run -> {out_path}")

    lock = threading.Lock()

    def work(job):
        key, item, condition, seed = job
        model, extra = model_spec(cfg, args.size, condition)
        record = {
            "key": key, "set": args.set, "size": args.size, "item_id": item["id"],
            "kind": item["kind"], "category": item["category"], "prompt": item["prompt"],
            "condition": condition, "model": model, "seed": seed, "generation": gen,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        try:
            record.update(client.chat(model, [{"role": "user", "content": item["prompt"]}],
                                      max_tokens=gen["max_tokens"], temperature=gen["temperature"],
                                      top_p=gen["top_p"], seed=seed, extra_body=extra))
        except Exception as e:
            record["error"] = str(e)
        with lock, out_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    started = time.monotonic()
    errors = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for n, fut in enumerate(as_completed(pool.submit(work, j) for j in jobs), 1):
            r = fut.result()
            if r.get("error"):
                errors += 1
                print(f"[{n}/{len(jobs)}] ERROR {r['key']}: {r['error'][:200]}")
            elif n % 10 == 0 or n == len(jobs):
                print(f"[{n}/{len(jobs)}] {time.monotonic() - started:.0f}s, errors={errors}")
    print(f"Done. errors={errors}. Rerun the same command to retry failed generations.")


if __name__ == "__main__":
    main()
