import pandas as pd
from pathlib import Path
HERE = Path(__file__).resolve().parent

# 1. Charger le fichier
df = pd.read_csv(HERE / "data" / "processing" / "dataset_25k.csv")

# Vérifier que la colonne existe
if 'text' not in df.columns:
    print("❌ La colonne 'text' n'existe pas dans le fichier")
    exit()

print("Nombre total de lignes :", len(df))

# 2. Vérification des doublons EXACTS
duplicates_exact = df['text'].duplicated().sum()

print("\n=== Doublons exacts ===")
print("Nombre de textes dupliqués :", duplicates_exact)

if duplicates_exact == 0:
    print("✅ Aucun doublon exact")
else:
    print("⚠️ Il existe des doublons exacts")

# 3. Vérification après nettoyage (plus robuste)
df['text_clean'] = df['text'].astype(str).str.strip().str.lower()

duplicates_clean = df['text_clean'].duplicated().sum()

print("\n=== Doublons après nettoyage (trim + lower) ===")
print("Nombre de textes dupliqués :", duplicates_clean)

if duplicates_clean == 0:
    print("✅ Aucun doublon après nettoyage")
else:
    print("⚠️ Il existe des doublons après nettoyage")

# 4. Afficher les doublons (optionnel)
print("\n=== Exemples de doublons ===")

dup_rows = df[df['text_clean'].duplicated(keep=False)]

if len(dup_rows) == 0:
    print("Aucun doublon à afficher")
else:
    print(dup_rows[['text']].head(10))  # afficher 10 exemples

# 5. (Optionnel) Sauvegarder les doublons dans un fichier
dup_rows.to_csv(HERE / "data" / "processing" / "duplicates_found.csv", index=False)

print("\n📁 Fichier des doublons sauvegardé : data/processing/duplicates_found.csv")