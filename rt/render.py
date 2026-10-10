import base64
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "data" / "images"
AUDIO = ROOT / "data" / "audio"


def render(items, style):
    """Render each item's prompt as a PNG (Windows System.Drawing). Returns {id: path}."""
    out_dir = IMAGES / style
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump([{"id": it["id"], "text": it["prompt"]} for it in items], f, ensure_ascii=False)
        manifest = f.name
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
         str(Path(__file__).with_name("render.ps1")), "-InJson", manifest, "-OutDir", str(out_dir),
         "-Style", style],
        check=True,
    )
    Path(manifest).unlink(missing_ok=True)
    return {it["id"]: out_dir / f"{it['id']}.png" for it in items}


def speak(items, voice):
    """Synthesize each item's prompt as a WAV (Windows System.Speech). Returns {id: path}."""
    out_dir = AUDIO / voice
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump([{"id": it["id"], "text": it["prompt"]} for it in items], f, ensure_ascii=False)
        manifest = f.name
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
         str(Path(__file__).with_name("tts.ps1")), "-InJson", manifest, "-OutDir", str(out_dir),
         "-Voice", voice],
        check=True,
    )
    Path(manifest).unlink(missing_ok=True)
    return {it["id"]: out_dir / f"{it['id']}.wav" for it in items}


def image_part(path):
    b64 = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}


def audio_part(path):
    b64 = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return {"type": "input_audio", "input_audio": {"data": b64, "format": "wav"}}
