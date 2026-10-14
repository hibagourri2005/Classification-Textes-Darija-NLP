"""
csv_to_json.py
--------------
Convertir un fichier CSV en JSON.

Usage:
  python csv_to_json.py --csv data.csv [--out output.json] [--orient records]

Arguments:
  --csv      Chemin vers le fichier CSV
  --out      Chemin du fichier JSON de sortie (défaut: même nom que le CSV)
  --orient   Format de sortie JSON :
               records  → [ {col: val, ...}, ... ]  (défaut)
               index    → { index: {col: val}, ... }
               values   → [ [val, ...], ... ]
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def csv_to_json(csv_path: Path, out_path: Path, orient: str) -> None:

    # Lire le CSV
    df = pd.read_csv(csv_path, dtype=str)
    print(f"[CSV]  Chargé {len(df)} lignes, {len(df.columns)} colonnes")
    print(f"[CSV]  Colonnes : {list(df.columns)}")

    # Remplacer les valeurs NaN par None (→ null en JSON)
    df = df.where(pd.notna(df), None)

    # Convertir selon l'orientation choisie
    if orient == "records":
        data = df.to_dict(orient="records")
    elif orient == "index":
        data = df.to_dict(orient="index")
    elif orient == "values":
        data = df.values.tolist()
    else:
        print(f"[ERROR] Orient inconnu: '{orient}'", file=sys.stderr)
        sys.exit(1)

    # Écrire le JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OUT]  Fichier JSON écrit → '{out_path}'")
    print(f"[OUT]  {len(data)} entrées exportées")


def main():
    parser = argparse.ArgumentParser(description="Convertir un CSV en JSON")
    parser.add_argument("--csv",    required=True,    help="Chemin vers le fichier CSV")
    parser.add_argument("--out",    default=None,     help="Chemin du fichier JSON de sortie")
    parser.add_argument("--orient", default="records",
                        choices=["records", "index", "values"],
                        help="Format JSON (défaut: records)")
    args = parser.parse_args()

    csv_path = Path(args.csv)

    if not csv_path.is_file():
        print(f"[ERROR] Fichier CSV introuvable : '{csv_path}'", file=sys.stderr)
        sys.exit(1)

    # Nom de sortie par défaut : même nom que le CSV avec extension .json
    out_path = Path(args.out) if args.out else csv_path.with_suffix(".json")

    csv_to_json(csv_path, out_path, args.orient)
    print("\nTerminé ✓")


if __name__ == "__main__":
    main()
