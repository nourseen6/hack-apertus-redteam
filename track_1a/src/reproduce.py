"""Offline check of the committed audio finding. No API key and no network.

Prints the rates stored in the finding file and checks the JSON against the
field limits in findings/findings.schema. A live regeneration is a separate
command: python experiments/b_carrier/run.py, from the repository root.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
FINDING = HERE / "findings" / "audio_refusal_gap.json"
SCHEMA = HERE / "findings" / "findings.schema"

LIMITS = {
    "overview": 1000,
    "desired_behavior": 1000,
    "observed_behavior": 1000,
    "self_assessed_severity_justification": 500,
    "self_assessed_breadth_justification": 500,
}


def main():
    finding = json.loads(FINDING.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    allowed = set(schema["properties"])
    extra = set(finding) - allowed
    if extra:
        sys.exit(f"unexpected fields: {sorted(extra)}")
    summary = finding["issue_summary"]
    for key, limit in LIMITS.items():
        if len(summary[key]) > limit:
            sys.exit(f"{key} exceeds {limit}")
    if not finding["apertus_response_walkthroughs"]:
        sys.exit("no walkthroughs")
    if "name" not in finding["model"]:
        sys.exit("model.name missing")
    print(finding["issue_title"])
    print("model:", finding["model"]["name"], "|", finding["model"]["version"])
    print("endpoint:", finding["environment"]["endpoint"])
    print("severity", summary["self_assessed_severity"], "| breadth", summary["self_assessed_breadth"])
    print()
    print(summary["overview"])
    print()
    print(f"{len(finding['apertus_response_walkthroughs'])} walkthroughs, schema fields ok")
    print("This command replays the committed finding. It does not call the model.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
