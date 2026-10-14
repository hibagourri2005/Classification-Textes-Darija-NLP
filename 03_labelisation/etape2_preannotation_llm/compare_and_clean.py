"""python compare_and_clean.py dataset_total_clean.csv mon_data.json"""

import csv
import json
import argparse
from pathlib import Path


def load_csv_ids(csv_path: str) -> set:
    """Charge tous les IDs depuis le fichier CSV."""
    ids = set()
    # utf-8-sig gère automatiquement le BOM (ï»¿) souvent présent dans les CSV Windows/Excel
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        # Détecter automatiquement le séparateur (virgule ou point-virgule)
        sample = f.read(2048)
        f.seek(0)
        delimiter = ';' if sample.count(';') > sample.count(',') else ','
        reader = csv.DictReader(f, delimiter=delimiter)
        # Afficher les colonnes détectées pour debug
        first_row = next(reader, None)
        if first_row is None:
            raise ValueError("Le fichier CSV est vide.")
        columns = list(first_row.keys())
        print(f"   → Colonnes détectées : {columns}")
        print(f"   → Séparateur utilisé : '{delimiter}'")
        if 'id' not in first_row:
            raise ValueError(f"Colonne 'id' introuvable. Colonnes disponibles : {columns}")
        ids.add(first_row['id'].strip())
        for row in reader:
            ids.add(row['id'].strip())
    return ids


def load_json(json_path: str) -> list:
    """Charge le fichier JSON (liste d'objets)."""
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Le fichier JSON doit contenir une liste d'objets.")
    return data


def compare_and_clean(csv_path: str, json_path: str, output_path: str = None):
    """
    Compare les IDs du CSV et du JSON.
    Supprime du JSON les entrées dont l'ID n'existe pas dans le CSV.
    """
    print(f"📂 Chargement du CSV  : {csv_path}")
    csv_ids = load_csv_ids(csv_path)
    print(f"   → {len(csv_ids)} IDs trouvés dans le CSV")

    print(f"📂 Chargement du JSON : {json_path}")
    json_data = load_json(json_path)
    print(f"   → {len(json_data)} entrées trouvées dans le JSON")

    # Filtrer les entrées dont l'ID existe dans le CSV
    cleaned_data = []
    removed = []

    for entry in json_data:
        entry_id = str(entry.get('id', '')).strip()
        if entry_id in csv_ids:
            cleaned_data.append(entry)
        else:
            removed.append(entry_id)

    # Rapport
    print(f"\n📊 Résultats :")
    print(f"   ✅ Entrées conservées : {len(cleaned_data)}")
    print(f"   ❌ Entrées supprimées : {len(removed)}")

    if removed:
        print(f"\n🗑️  IDs supprimés du JSON :")
        for rid in removed:
            print(f"   - {rid}")

    # Sauvegarde
    if output_path is None:
        p = Path(json_path)
        output_path = str(p.parent / (p.stem + "_cleaned" + p.suffix))

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

    print(f"\n💾 Fichier JSON nettoyé sauvegardé : {output_path}")
    return cleaned_data, removed


def main():
    parser = argparse.ArgumentParser(
        description="Compare un CSV et un JSON, supprime du JSON les IDs absents du CSV."
    )
    parser.add_argument("csv_file", help="Chemin vers le fichier CSV")
    parser.add_argument("json_file", help="Chemin vers le fichier JSON")
    parser.add_argument(
        "--output", "-o",
        help="Chemin du fichier JSON nettoyé (défaut: <json_file>_cleaned.json)",
        default=None
    )
    args = parser.parse_args()

    compare_and_clean(args.csv_file, args.json_file, args.output)


if __name__ == "__main__":
    main()