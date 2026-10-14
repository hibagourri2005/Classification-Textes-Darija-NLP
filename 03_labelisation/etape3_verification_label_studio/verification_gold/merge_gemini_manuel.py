"""
merge_gemini_manuel.py
-----------------------
Fusionne deux fichiers JSON Label Studio :
  - gemini_file  : contient gemini_label dans data
  - manuel_file  : contient manuel_label dans data

Le résultat est un fichier JSON avec les deux labels dans data :
  {
    "data": {
      "text": "...",
      "entry_id": "darija_049694",
      "gemini_label": "food",
      "manuel_label": "sports"   ← ajouté depuis le fichier manuel
    },
    "predictions": [...]
  }

Usage:
  python merge_gemini_manuel.py --gemini gemini.json --manuel manuel.json --out merged.json
"""

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> list:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Le fichier {path} doit être un tableau JSON (liste)")
    print(f"[LOAD] {len(data)} entrées chargées depuis '{path}'")
    return data


def main():
    parser = argparse.ArgumentParser(description="Fusionner fichiers Gemini et Manuel")
    parser.add_argument("--gemini", required=True, help="Fichier JSON Gemini")
    parser.add_argument("--manuel", required=True, help="Fichier JSON Manuel")
    parser.add_argument("--out",    required=True, help="Fichier JSON de sortie")
    args = parser.parse_args()

    gemini_entries = load_json(Path(args.gemini))
    manuel_entries = load_json(Path(args.manuel))

    # Construire un index { entry_id → manuel_label } depuis le fichier manuel
    manuel_index = {}
    for entry in manuel_entries:
        entry_id     = entry.get("data", {}).get("entry_id")
        manuel_label = entry.get("data", {}).get("manuel_label")
        if entry_id and manuel_label:
            manuel_index[entry_id] = manuel_label

    print(f"[INDEX] {len(manuel_index)} labels manuels indexés")

    # Fusionner
    merged        = []
    found         = 0
    not_found     = 0

    for entry in gemini_entries:
        entry_id = entry.get("data", {}).get("entry_id")
        if entry_id and entry_id in manuel_index:
            entry["data"]["manuel_label"] = manuel_index[entry_id]
            found += 1
        else:
            entry["data"]["manuel_label"] = None  # champ vide si pas trouvé
            not_found += 1
        merged.append(entry)

    # Sauvegarder
    out_path = Path(args.out)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"\n{'─'*45}")
    print(f"  Total entrées       : {len(merged)}")
    print(f"  Labels fusionnés    : {found}")
    print(f"  Sans label manuel   : {not_found}")
    print(f"{'─'*45}")
    print(f"[OUT]  Fichier fusionné → '{out_path}'")
    print("\nTerminé ✓")


if __name__ == "__main__":
    main()
