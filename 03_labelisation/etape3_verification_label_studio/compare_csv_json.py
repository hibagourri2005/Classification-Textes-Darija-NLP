"""
compare_csv_json.py
--------------------
Compare IDs between a CSV (gold) file and a JSON (all by gemini) file.

Outputs:
  - common_ids.json   → entries from the JSON whose ID exists in the CSV
  - remaining_ids.json → entries from the JSON whose ID does NOT exist in the CSV

Usage:
  python compare_csv_json.py --csv data.csv --json data.json [--out-dir .]

Arguments:
  --csv      Path to the CSV file (must have an 'id' column)
  --json     Path to the JSON file (array of objects, each with an 'id' field)
  --out-dir  Directory where output files will be written (default: current dir)
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def load_csv_ids(csv_path: Path) -> set:
    """Load the CSV and return a set of all values in the 'id' column."""
    df = pd.read_csv(csv_path, usecols=["id"], dtype=str)
    ids = set(df["id"].dropna().str.strip())
    print(f"[CSV]  Loaded {len(ids)} unique IDs from '{csv_path}'")
    return ids


def load_json_entries(json_path: Path) -> list:
    """Load the JSON file and return the list of entry objects."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Accept either a bare list or a dict that wraps a list
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        # Try common wrapper keys
        for key in ("data", "items", "entries", "records"):
            if key in data and isinstance(data[key], list):
                entries = data[key]
                print(f"[JSON] Found entries under key '{key}'")
                break
        else:
            raise ValueError(
                "JSON root is a dict but no known list key was found. "
                "Expected a JSON array or a dict with a 'data'/'items' key."
            )
    else:
        raise ValueError(f"Unexpected JSON root type: {type(data)}")

    print(f"[JSON] Loaded {len(entries)} entries from '{json_path}'")
    return entries


def compare_and_split(csv_ids: set, json_entries: list) -> tuple[list, list]:
    """
    Split json_entries into two lists:
      - common   : entries whose 'id' is present in csv_ids
      - remaining: entries whose 'id' is NOT in csv_ids
    """
    common = []
    remaining = []
    missing_id_count = 0

    for entry in json_entries:
        entry_id = str(entry.get("id", "")).strip()
        if not entry_id:
            missing_id_count += 1
            remaining.append(entry)
            continue

        if entry_id in csv_ids:
            common.append(entry)
        else:
            remaining.append(entry)

    if missing_id_count:
        print(f"[WARN] {missing_id_count} JSON entries had no 'id' field → placed in remaining")

    return common, remaining


def save_json(data: list, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OUT]  Wrote {len(data):>6} entries → '{path}'")


def main():
    parser = argparse.ArgumentParser(
        description="Compare a CSV and a JSON file by their 'id' field."
    )
    parser.add_argument("--csv",     required=True, help="Path to the CSV file")
    parser.add_argument("--json",    required=True, help="Path to the JSON file")
    parser.add_argument("--out-dir", default=".",   help="Output directory (default: current dir)")
    args = parser.parse_args()

    csv_path  = Path(args.csv)
    json_path = Path(args.json)
    out_dir   = Path(args.out_dir)

    # ── Validate inputs ──────────────────────────────────────────────────────
    if not csv_path.is_file():
        print(f"[ERROR] CSV file not found: '{csv_path}'", file=sys.stderr)
        sys.exit(1)
    if not json_path.is_file():
        print(f"[ERROR] JSON file not found: '{json_path}'", file=sys.stderr)
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    # ── Load data ─────────────────────────────────────────────────────────────
    csv_ids      = load_csv_ids(csv_path)
    json_entries = load_json_entries(json_path)

    # ── Compare ───────────────────────────────────────────────────────────────
    common, remaining = compare_and_split(csv_ids, json_entries)

    # ── Summary ───────────────────────────────────────────────────────────────
    total = len(json_entries)
    print(
        f"\n{'─'*45}\n"
        f"  Total JSON entries : {total}\n"
        f"  Common (in CSV)    : {len(common)}  "
        f"({len(common)/total*100:.1f}%)\n"
        f"  Remaining (not in CSV): {len(remaining)}  "
        f"({len(remaining)/total*100:.1f}%)\n"
        f"{'─'*45}"
    )

    # ── Save outputs ──────────────────────────────────────────────────────────
    save_json(common,    out_dir / "common_ids.json")
    save_json(remaining, out_dir / "remaining_ids.json")

    print("\nDone ✓")


if __name__ == "__main__":
    main()
