"""
merge_partners.py
Fusionne deux datasets CSV avec des structures différentes en un seul fichier unifié.

Structure cible commune :
  id, text, source_type, domain, channel_name, published_at, label, language

Usage :
    python merge_partners.py --file1 mon_dataset.csv --file2 dataset_partenaire.csv
    python merge_partners.py  (utilise les noms par défaut)
"""

import argparse
import pandas as pd
import json
from pathlib import Path

# -----------------------------------------------------------------------
# Structure cible unifiée
# -----------------------------------------------------------------------
FINAL_COLUMNS = [
    "id",
    "text",
    "source_type",
    "domain",
    "channel_name",
    "published_at",
    "label",
    "language"
]


def normalize_file1(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise le fichier de TON binôme (structure 1) :
    id, text, source_type, domain, channel_name, channel_handle,
    video_id, video_title, published_at, label, language
    """
    print(f"  Colonnes fichier 1 : {list(df.columns)}")
    out = pd.DataFrame()
    out["text"]         = df["text"]
    out["source_type"]  = df["source_type"]
    out["domain"]       = df["domain"]
    out["channel_name"] = df["channel_name"]
    out["published_at"] = df["published_at"].astype(str)
    out["label"]        = df["label"]
    out["language"]     = df.get("language", "darija")
    return out


def normalize_file2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise le fichier de l'AUTRE binôme (structure 2) :
    id, text, source_type, channel, category, url, date, label, language

    Mapping :
      channel   → channel_name
      category  → domain
      date      → published_at
    """
    print(f"  Colonnes fichier 2 : {list(df.columns)}")
    out = pd.DataFrame()
    out["text"]         = df["text"]
    out["source_type"]  = df["source_type"].str.lower().str.replace("_", " ")
    out["domain"]       = df["category"].str.lower().str.strip()
    out["channel_name"] = df["channel"]
    out["published_at"] = df["date"].astype(str)
    out["label"]        = df.get("label", df["category"].str.lower().str.strip())
    out["language"]     = df.get("language", "darija")
    return out


def merge(file1: Path, file2: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Lire les deux fichiers
    # -----------------------------------------------------------------------
    print(f"\n📂 Lecture fichier 1 : {file1.name}")
    df1_raw = pd.read_csv(file1, encoding="utf-8")
    print(f"   → {len(df1_raw)} lignes")

    print(f"\n📂 Lecture fichier 2 : {file2.name}")
    df2_raw = pd.read_csv(file2, encoding="utf-8")
    print(f"   → {len(df2_raw)} lignes")

    # -----------------------------------------------------------------------
    # Normaliser
    # -----------------------------------------------------------------------
    print("\n🔄 Normalisation fichier 1...")
    df1 = normalize_file1(df1_raw)

    print("🔄 Normalisation fichier 2...")
    df2 = normalize_file2(df2_raw)

    # -----------------------------------------------------------------------
    # Fusionner
    # -----------------------------------------------------------------------
    df = pd.concat([df1, df2], ignore_index=True)
    print(f"\n✓ Total après fusion : {len(df)} textes")

    # -----------------------------------------------------------------------
    # Nettoyage
    # -----------------------------------------------------------------------
    # Supprimer lignes sans texte
    df = df[df["text"].notna() & (df["text"].str.strip() != "")]

    # Supprimer doublons sur le texte
    before = len(df)
    df = df.drop_duplicates(subset=["text"])
    print(f"✓ Doublons supprimés : {before - len(df)}")
    print(f"✓ Total final        : {len(df)} textes")

    # Normaliser le label (minuscules, sans espaces)
    df["label"] = df["label"].astype(str).str.lower().str.strip()
    df["language"] = "darija"

    # Réinitialiser les IDs
    df["id"] = [f"darija_{i:06d}" for i in range(len(df))]
    df = df[FINAL_COLUMNS]

    # -----------------------------------------------------------------------
    # Export CSV
    # -----------------------------------------------------------------------
    csv_path = output_dir / "dataset_merged.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"\n✅ CSV exporté : {csv_path}")

    # -----------------------------------------------------------------------
    # Export JSON
    # -----------------------------------------------------------------------
    json_path = output_dir / "dataset_merged.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
    print(f"✅ JSON exporté : {json_path}")

    # -----------------------------------------------------------------------
    # Rapport
    # -----------------------------------------------------------------------
    print("\n" + "=" * 55)
    print("  RÉSUMÉ DE LA FUSION")
    print("=" * 55)
    print(f"  Fichier 1 ({file1.name[:25]:25s}) : {len(df1):6d} textes")
    print(f"  Fichier 2 ({file2.name[:25]:25s}) : {len(df2):6d} textes")
    print(f"  {'─'*45}")
    print(f"  Total fusionné                    : {len(df):6d} textes")

    print(f"\n  Par domaine :")
    for domain, count in df["domain"].value_counts().items():
        pct = count / len(df) * 100
        bar = "█" * int(pct / 3)
        print(f"    {domain:20s} : {count:5d} ({pct:4.1f}%) {bar}")

    print(f"\n  Par source :")
    for src, count in df["source_type"].value_counts().items():
        print(f"    {src:30s} : {count:5d}")

    print(f"\n  Labels présents :")
    for label, count in df["label"].value_counts().items():
        print(f"    {label:20s} : {count:5d}")

    print("=" * 55)
    print(f"\n📁 Fichiers générés dans '{output_dir}/' :")
    print(f"   dataset_merged.csv   ({csv_path.stat().st_size // 1024} Ko)")
    print(f"   dataset_merged.json  ({json_path.stat().st_size // 1024} Ko)\n")


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fusion de deux datasets Darija")
    parser.add_argument(
        "--file1",
        type=Path,
        default=Path("data/final/dataset_final.csv"),
        help="Ton fichier CSV (structure 1 — avec domain, channel_name...)"
    )
    parser.add_argument(
        "--file2",
        type=Path,
        default=Path("data/partner/youtube_raw.csv"),
        help="Le fichier CSV du partenaire (structure 2 — avec channel, category...)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/merged"),
        help="Dossier de sortie (défaut : data/merged/)"
    )
    args = parser.parse_args()

    if not args.file1.exists():
        print(f"❌ Fichier 1 introuvable : {args.file1}")
        print("   Vérifie le chemin avec --file1 <chemin>")
        exit(1)
    if not args.file2.exists():
        print(f"❌ Fichier 2 introuvable : {args.file2}")
        print("   Vérifie le chemin avec --file2 <chemin>")
        exit(1)

    merge(args.file1, args.file2, args.output)