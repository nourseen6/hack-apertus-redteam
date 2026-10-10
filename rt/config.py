import json
from pathlib import Path

from rt.client import ChatClient

ROOT = Path(__file__).resolve().parent.parent


def load_config(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def make_client(cfg):
    p = cfg["provider"]
    return ChatClient(p["base_url"], p["api_key_env"], p.get("user_agent", "hack-apertus-redteam/0.1"))


def model_spec(cfg, size, condition):
    """Return (model_id, extra_body) for a size ("8b") and condition ("off"/"on")."""
    spec = cfg["models"][size][condition]
    if isinstance(spec, str):
        return spec, None
    return spec["model"], spec.get("extra_body")


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
