"""python find_missing_ids.py dataset_total_clean.csv mon_data.json --output manquants.json"""

import csv
import json
import argparse
from pathlib import Path


def load_csv(csv_path: str) -> dict:
    """Charge le CSV et retourne un dict {id: row}."""
    rows = {}
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = ';' if sample.count(';') > sample.count(',') else ','
        reader = csv.DictReader(f, delimiter=delimiter)

        first_row = next(reader, None)
        if first_row is None:
            raise ValueError("Le fichier CSV est vide.")

        columns = list(first_row.keys())
        print(f"   → Colonnes détectées : {columns}")
        print(f"   → Séparateur utilisé : '{delimiter}'")

        if 'id' not in first_row:
            raise ValueError(f"Colonne 'id' introuvable. Colonnes disponibles : {columns}")

        rows[first_row['id'].strip()] = first_row
        for row in reader:
            rows[row['id'].strip()] = row

    return rows


def load_json_ids(json_path: str) -> set:
    """Charge le JSON et retourne l'ensemble des IDs présents."""
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Le fichier JSON doit contenir une liste d'objets.")
    return {str(entry.get('id', '')).strip() for entry in data}


def find_missing(csv_path: str, json_path: str, output_path: str = None):
    """
    Trouve les IDs présents dans le CSV mais absents du JSON.
    Génère un fichier JSON avec ces entrées manquantes.
    """
    print(f"📂 Chargement du CSV  : {csv_path}")
    csv_data = load_csv(csv_path)
    print(f"   → {len(csv_data)} entrées trouvées dans le CSV\n")

    print(f"📂 Chargement du JSON : {json_path}")
    json_ids = load_json_ids(json_path)
    print(f"   → {len(json_ids)} IDs trouvés dans le JSON\n")

    # IDs dans CSV mais pas dans JSON
    missing_ids = set(csv_data.keys()) - json_ids
    print(f"📊 Résultats :")
    print(f"   ✅ IDs en commun         : {len(set(csv_data.keys()) & json_ids)}")
    print(f"   ❌ IDs manquants dans JSON: {len(missing_ids)}")

    # Construire la liste de sortie
    output = []
    for mid in sorted(missing_ids):
        row = csv_data[mid]
        output.append({
            "id": mid,
            "text_normalized": row.get("text_normalized", "").strip(),
            "domain": row.get("domain", "").strip() or None,
            "label": row.get("label", None) or None
        })

    # Sauvegarde
    if output_path is None:
        p = Path(json_path)
        output_path = str(p.parent / "missing_ids.json")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Fichier sauvegardé : {output_path}")
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Trouve les IDs présents dans le CSV mais absents du JSON."
    )
    parser.add_argument("csv_file", help="Chemin vers le fichier CSV")
    parser.add_argument("json_file", help="Chemin vers le fichier JSON")
    parser.add_argument(
        "--output", "-o",
        help="Chemin du fichier JSON de sortie (défaut: missing_ids.json)",
        default=None
    )
    args = parser.parse_args()

    find_missing(args.csv_file, args.json_file, args.output)


if __name__ == "__main__":
    main()
