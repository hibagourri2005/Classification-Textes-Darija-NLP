"""python check_duplicates.py mon_data.json"""

import json
import argparse
from collections import Counter


def check_duplicates(json_path: str, output_path: str = None):
    """Vérifie les doublons dans un fichier JSON par ID."""

    print(f"📂 Chargement du JSON : {json_path}")
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Le fichier JSON doit contenir une liste d'objets.")

    print(f"   → {len(data)} entrées trouvées\n")

    # Compter les occurrences de chaque ID
    id_counts = Counter(str(entry.get('id', '')).strip() for entry in data)
    duplicates = {id_: count for id_, count in id_counts.items() if count > 1}

    print(f"📊 Résultats :")
    print(f"   🔢 Total entrées       : {len(data)}")
    print(f"   ✅ IDs uniques         : {len(id_counts)}")
    print(f"   ❌ IDs en doublon      : {len(duplicates)}")
    total_extra = sum(c - 1 for c in duplicates.values())
    print(f"   ♻️  Entrées redondantes : {total_extra}")

    if not duplicates:
        print("\n✅ Aucun doublon trouvé !")
        return

    print(f"\n🗂️  Détail des doublons :")
    print(f"   {'ID':<30} {'Occurrences':>10}")
    print(f"   {'-'*30} {'-'*10}")
    for id_, count in sorted(duplicates.items()):
        print(f"   {id_:<30} {count:>10}")

    # Optionnel : sauvegarder un JSON dédupliqué
    if output_path:
        seen = set()
        deduped = []
        for entry in data:
            eid = str(entry.get('id', '')).strip()
            if eid not in seen:
                seen.add(eid)
                deduped.append(entry)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(deduped, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Fichier dédupliqué sauvegardé : {output_path}")
        print(f"   → {len(deduped)} entrées conservées (première occurrence gardée)")


def main():
    parser = argparse.ArgumentParser(
        description="Vérifie les doublons dans un fichier JSON par ID."
    )
    parser.add_argument("json_file", help="Chemin vers le fichier JSON")
    parser.add_argument(
        "--fix", "-f",
        help="Chemin de sortie pour sauvegarder le JSON dédupliqué",
        default=None
    )
    args = parser.parse_args()

    check_duplicates(args.json_file, args.fix)


if __name__ == "__main__":
    main()
