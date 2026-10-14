"""
merge_all.py
Fusionne tous les fichiers CSV de data/raw/ en un seul dataset final.
Lance : python merge_all.py
"""

import pandas as pd
import json
import glob
from pathlib import Path

RAW_DIR = Path("data/raw")
FINAL_DIR = Path("data/final")
FINAL_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------
# 1. Lire tous les CSV de data/raw/
# -----------------------------------------------------------------------
all_files = glob.glob(str(RAW_DIR / "**" / "*.csv"), recursive=True)

if not all_files:
    print("❌ Aucun fichier CSV trouvé dans data/raw/")
    print("   Lance d'abord : python main.py --domains religion food entertainment miscill")
    exit()

print(f"📂 Fichiers trouvés : {len(all_files)}")
for f in all_files:
    df_tmp = pd.read_csv(f)
    print(f"   {f} → {len(df_tmp)} textes")

# -----------------------------------------------------------------------
# 2. Fusionner
# -----------------------------------------------------------------------
df = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)
print(f"\n✓ Total avant nettoyage : {len(df)} textes")

# -----------------------------------------------------------------------
# 3. Supprimer les doublons
# -----------------------------------------------------------------------
before = len(df)
df = df.drop_duplicates(subset=["text"])
print(f"✓ Doublons supprimés : {before - len(df)}")
print(f"✓ Total final : {len(df)} textes")

# -----------------------------------------------------------------------
# 4. Réinitialiser les IDs
# -----------------------------------------------------------------------
df["id"] = [f"darija_{i:06d}" for i in range(len(df))]
df["language"] = "darija"

# -----------------------------------------------------------------------
# 5. Export CSV
# -----------------------------------------------------------------------
csv_path = FINAL_DIR / "dataset_final.csv"
df.to_csv(csv_path, index=False, encoding="utf-8")
print(f"\n✅ CSV exporté : {csv_path}")

# -----------------------------------------------------------------------
# 6. Export JSON (pour Label Studio)
# -----------------------------------------------------------------------
json_path = FINAL_DIR / "dataset_final.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
print(f"✅ JSON exporté : {json_path}")

# -----------------------------------------------------------------------
# 7. Rapport statistiques
# -----------------------------------------------------------------------
stats_path = FINAL_DIR / "stats_report.txt"
lines = [
    "=" * 60,
    "RAPPORT DATASET DARIJA — FUSION COMPLÈTE",
    "=" * 60,
    f"Total textes          : {len(df)}",
    f"Textes uniques        : {df['text'].nunique()}",
    f"Longueur moy. (chars) : {df['text'].str.len().mean():.1f}",
    f"Longueur med. (chars) : {df['text'].str.len().median():.1f}",
    "",
    "--- Par domaine ---",
]
for domain, count in df["domain"].value_counts().items():
    pct = count / len(df) * 100
    lines.append(f"  {domain:20s} : {count:6d} ({pct:.1f}%)")

lines += ["", "--- Par type de source ---"]
for src, count in df["source_type"].value_counts().items():
    pct = count / len(df) * 100
    lines.append(f"  {src:30s} : {count:6d} ({pct:.1f}%)")

lines += ["", "--- Par chaîne ---"]
for ch, count in df["channel_name"].value_counts().items():
    lines.append(f"  {ch:35s} : {count:6d}")

with open(stats_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"✅ Rapport stats : {stats_path}")

# -----------------------------------------------------------------------
# 8. Résumé console
# -----------------------------------------------------------------------
print("\n" + "=" * 60)
print("RÉSUMÉ")
print("=" * 60)
print(f"{'Domaine':<20} {'Textes':>8} {'%':>6}")
print("-" * 36)
for domain, count in df["domain"].value_counts().items():
    pct = count / len(df) * 100
    print(f"{domain:<20} {count:>8} {pct:>5.1f}%")
print("-" * 36)
print(f"{'TOTAL':<20} {len(df):>8}")
print("=" * 60)
print(f"\n📁 Fichiers dans data/final/ :")
print(f"   dataset_final.csv   ({csv_path.stat().st_size // 1024} Ko)")
print(f"   dataset_final.json  ({json_path.stat().st_size // 1024} Ko)")
print(f"   stats_report.txt")
