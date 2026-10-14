"""python compare_ids.py dataset_total_clean.csv mon_data.json"""

import csv
import json
import argparse


def load_csv_ids(csv_path: str) -> set:
    """Charge les IDs depuis le fichier CSV."""
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


def load_json_ids(json_path: str) -> set:
    """Charge les IDs depuis le fichier JSON."""
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Le fichier JSON doit contenir une liste d'objets.")
    return {str(entry.get('id', '')).strip() for entry in data}


def compare_ids(csv_path: str, json_path: str):
    print(f"📂 Chargement du CSV  : {csv_path}")
    csv_ids = load_csv_ids(csv_path)
    print(f"   → {len(csv_ids)} IDs uniques dans le CSV")

    print(f"📂 Chargement du JSON : {json_path}")
    json_ids = load_json_ids(json_path)
    print(f"   → {len(json_ids)} IDs uniques dans le JSON\n")

    # Calculs
    common       = csv_ids & json_ids
    only_in_csv  = csv_ids - json_ids
    only_in_json = json_ids - csv_ids

    print("=" * 50)
    print(f"📊 RÉSUMÉ DE LA COMPARAISON")
    print("=" * 50)
    print(f"  ✅ IDs en commun (dans les deux)  : {len(common)}")
    print(f"  📄 IDs uniquement dans le CSV     : {len(only_in_csv)}")
    print(f"  📋 IDs uniquement dans le JSON    : {len(only_in_json)}")

    if len(common) == len(csv_ids) == len(json_ids):
        print("\n🎉 Les deux fichiers contiennent exactement les mêmes IDs !")
    else:
        print(f"\n⚠️  Les fichiers ne sont PAS identiques.")

    if only_in_csv:
        print(f"\n📄 IDs présents dans CSV mais absents du JSON ({len(only_in_csv)}) :")
        for id_ in sorted(only_in_csv):
            print(f"   - {id_}")

    if only_in_json:
        print(f"\n📋 IDs présents dans JSON mais absents du CSV ({len(only_in_json)}) :")
        for id_ in sorted(only_in_json):
            print(f"   - {id_}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare les IDs entre un fichier CSV et un fichier JSON."
    )
    parser.add_argument("csv_file", help="Chemin vers le fichier CSV")
    parser.add_argument("json_file", help="Chemin vers le fichier JSON")
    args = parser.parse_args()

    compare_ids(args.csv_file, args.json_file)


if __name__ == "__main__":
    main()
