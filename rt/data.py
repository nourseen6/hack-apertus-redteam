import csv
import io
import random
import urllib.request
from pathlib import Path

CACHE = Path(__file__).resolve().parent.parent / "data" / "cache"

SOURCES = {
    "strongreject_small": "https://raw.githubusercontent.com/alexandrasouly/strongreject/main/strongreject_dataset/strongreject_small_dataset.csv",
    "strongreject": "https://raw.githubusercontent.com/alexandrasouly/strongreject/main/strongreject_dataset/strongreject_dataset.csv",
    "xstest": "https://raw.githubusercontent.com/paul-rottger/xstest/main/xstest_prompts.csv",
}


def _fetch(name):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{name}.csv"
    if not path.exists():
        with urllib.request.urlopen(SOURCES[name], timeout=60) as resp:
            path.write_bytes(resp.read())
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8"))))


def load_set(name, limit=None, sample_seed=0):
    """Return items as dicts with id, kind, category, prompt.

    kind is "harmful" for items the model should refuse and "benign" for
    over-refusal controls.
    """
    if name in ("strongreject", "strongreject_small"):
        items = [
            {"id": f"{name}-{i:03d}", "kind": "harmful", "category": r["category"],
             "source": r["source"], "prompt": r["forbidden_prompt"]}
            for i, r in enumerate(_fetch(name))
        ]
    elif name == "xstest_safe":
        items = [
            {"id": f"xstest-{r['id']}", "kind": "benign", "category": r["type"],
             "source": "xstest", "prompt": r["prompt"]}
            for r in _fetch("xstest") if r["label"] == "safe"
        ]
    else:
        raise ValueError(f"Unknown set {name}")

    if limit and limit < len(items):
        items = random.Random(sample_seed).sample(items, limit)
        items.sort(key=lambda x: x["id"])
    return items
