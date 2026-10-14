"""python sync_json_to_csv.py dataset_total_clean.csv mon_data_clean.json --output mon_data_final.json"""

import csv
import json
import argparse


def load_csv_ids(csv_path: str) -> set:
    ids = set()
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = ';' if sample.count(';') > sample.count(',') else ','
        reader = csv.DictReader(f, delimiter=delimiter)
        first_row = next(reader, None)
        if first_row is None:
            raise ValueError("Le fichier CSV est vide.")
        if 'id' not in first_row:
            raise ValueError(f"Colonne 'id' introuvable. Colonnes : {list(first_row.keys())}")
        ids.add(first_row['id'].strip())
        for row in reader:
            ids.add(row['id'].strip())
    return ids


def sync_json_to_csv(csv_path: str, json_path: str, output_path: str = None):
    print(f"📂 Chargement du CSV  : {csv_path}")
    csv_ids = load_csv_ids(csv_path)
    print(f"   → {len(csv_ids)} IDs dans le CSV")

    print(f"📂 Chargement du JSON : {json_path}")
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    print(f"   → {len(data)} entrées dans le JSON\n")

    # Filtrer
    cleaned = [e for e in data if str(e.get('id', '')).strip() in csv_ids]
    removed = [str(e.get('id', '')).strip() for e in data if str(e.get('id', '')).strip() not in csv_ids]

    print(f"📊 Résultats :")
    print(f"   ✅ Entrées conservées : {len(cleaned)}")
    print(f"   ❌ Entrées supprimées : {len(removed)}")

    if removed:
        print(f"\n🗑️  IDs supprimés :")
        for rid in removed:
            print(f"   - {rid}")

    # Sauvegarde
    if output_path is None:
        output_path = json_path  # Écraser le fichier original

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Fichier sauvegardé : {output_path}")
    print(f"   → JSON et CSV contiennent maintenant les mêmes {len(cleaned)} IDs ✅")


def main():
    parser = argparse.ArgumentParser(
        description="Supprime du JSON les IDs absents du CSV."
    )
    parser.add_argument("csv_file", help="Chemin vers le fichier CSV")
    parser.add_argument("json_file", help="Chemin vers le fichier JSON")
    parser.add_argument("--output", "-o", help="Fichier de sortie (défaut: écrase le JSON)", default=None)
    args = parser.parse_args()

    sync_json_to_csv(args.csv_file, args.json_file, args.output)


if __name__ == "__main__":
    main()
