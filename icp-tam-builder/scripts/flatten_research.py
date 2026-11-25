#!/usr/bin/env python3
"""Flatten per-account research output into a CSV that score_accounts.py can read.

Usage:
    python flatten_research.py research.json [-o accounts.csv]

Input: a JSON list of objects, or JSON Lines (one object per line), in the shape the
classification prompt in references/scoring-and-validation.md returns:

    [{"domain": "example.com",
      "vertical_group": {"value": "dental_clinic", "source_url": "https://...",
                         "retrieved_on": "2026-11-17", "confidence": "high"},
      "hiring_front_desk": {"value": "yes", "source_url": "https://...",
                            "retrieved_on": "2026-11-17", "confidence": "medium"},
      "hiring_front_desk_date": {"value": "2026-11-01", "source_url": "https://...",
                                 "retrieved_on": "2026-11-17", "confidence": "medium"}}]

Output: one row per account. A field written as {value, source_url, retrieved_on,
confidence} becomes up to four columns: <field>, <field>__source, <field>__retrieved_on and
<field>__confidence. score_accounts.py reads <field>__confidence and lists rows whose gate or
heaviest rule rests on "low" confidence for a person to review. Plain values pass through.
Lists are joined with "; ". "unknown" stays "unknown", which the scorer treats as unknown.
Column names are the research field names, so they must match the scoring model's "field"
and "date_field" names exactly. See ../examples/research-output.json.
"""

import csv
import json
import sys


def die(msg):
    raise SystemExit(f"error: {msg}")


def load(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            text = f.read().strip()
    except OSError as e:
        die(f"cannot read {path} ({e.strerror})")
    try:
        if text.startswith("["):
            data = json.loads(text)
        else:
            data = [json.loads(line) for line in text.splitlines() if line.strip()]
    except json.JSONDecodeError as e:
        die(f"{path} is not valid JSON or JSON Lines ({e}). Comments are not allowed; "
            "copy examples/research-output.json instead.")
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        die(f"{path} must hold one JSON object per account")
    return data


def cell(v):
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    return "" if v is None else v


def flatten(record):
    row = {}
    for key, v in record.items():
        if isinstance(v, dict) and "value" in v:
            row[key] = cell(v.get("value"))
            row[f"{key}__source"] = cell(v.get("source_url"))
            row[f"{key}__retrieved_on"] = cell(v.get("retrieved_on"))
            if "confidence" in v:
                row[f"{key}__confidence"] = cell(v.get("confidence"))
        else:
            row[key] = cell(v)
    return row


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    args = sys.argv[1:]
    out = None
    if "-o" in args:
        i = args.index("-o")
        if i + 1 >= len(args):
            die("-o needs a file name, for example -o accounts.csv")
        out = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        raise SystemExit(__doc__)
    rows = [flatten(r) for r in load(args[0])]
    cols = []
    for r in rows:
        cols += [k for k in r if k not in cols]
    out = out or args[0].rsplit(".", 1)[0] + "_flat.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"Flattened {len(rows)} accounts, {len(cols)} columns -> {out}")


if __name__ == "__main__":
    main()
