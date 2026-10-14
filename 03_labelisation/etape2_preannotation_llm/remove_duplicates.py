"""python remove_duplicates.py mon_data.json --output mon_data_clean.json"""

import json
import argparse


def remove_duplicates(json_path: str, output_path: str = None):
    """Supprime les doublons d'un fichier JSON par ID (garde la première occurrence)."""

    print(f"📂 Chargement du JSON : {json_path}")
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    print(f"   → {len(data)} entrées avant déduplication\n")

    seen = set()
    deduped = []
    removed = []

    for entry in data:
        eid = str(entry.get('id', '')).strip()
        if eid not in seen:
            seen.add(eid)
            deduped.append(entry)
        else:
            removed.append(eid)

    print(f"📊 Résultats :")
    print(f"   ✅ Entrées conservées : {len(deduped)}")
    print(f"   ❌ Doublons supprimés : {len(removed)}")

    if removed:
        print(f"\n🗑️  IDs dédupliqués :")
        for rid in removed:
            print(f"   - {rid}")

    # Sauvegarde
    if output_path is None:
        output_path = json_path  # Écraser le fichier original

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Fichier sauvegardé : {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Supprime les doublons d'un fichier JSON par ID."
    )
    parser.add_argument("json_file", help="Chemin vers le fichier JSON")
    parser.add_argument(
        "--output", "-o",
        help="Fichier de sortie (défaut: écrase le fichier original)",
        default=None
    )
    args = parser.parse_args()

    remove_duplicates(args.json_file, args.output)


if __name__ == "__main__":
    main()
