"""Confirm the endpoint serves both conditions and that the thinking span is separable.

Run this before any experiment. If the thinking condition returns parse "none",
the provider is hiding or stripping the span and Experiment A cannot run there.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.stdout.reconfigure(encoding="utf-8")

from rt.config import load_config, make_client, model_spec

PROBE = "A bat and a ball cost 1.10 CHF together. The bat costs 1 CHF more than the ball. What does the ball cost?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(Path(__file__).with_name("config.json")))
    ap.add_argument("--size", default="8b")
    args = ap.parse_args()

    cfg = load_config(args.config)
    client = make_client(cfg)

    ids = sorted(m["id"] for m in client.models() if "apertus" in m["id"].lower())
    print("Apertus models on endpoint:", ", ".join(ids) or "(none)")

    for condition in ("off", "on"):
        model, extra = model_spec(cfg, args.size, condition)
        out = client.chat(model, [{"role": "user", "content": PROBE}], max_tokens=2048,
                          temperature=0.0, extra_body=extra)
        print(f"\n== {condition}: {model} (served as {out['served_model']})")
        print(f"parse={out['parse']} finish={out['finish_reason']} usage={out['usage']}")
        print(f"reasoning chars={len(out['reasoning'])}: {out['reasoning'][:300]!r}")
        print(f"answer: {out['answer'][:300]!r}")

    if out["parse"] == "none":
        print("\nWARNING: no thinking span found in the 'on' condition. Do not run Experiment A on this endpoint.")


if __name__ == "__main__":
    main()
