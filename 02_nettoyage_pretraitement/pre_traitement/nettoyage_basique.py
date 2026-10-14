import pandas as pd
from pathlib import Path
HERE = Path(__file__).resolve().parent

# Charger dataset
df = pd.read_csv(HERE / "data" / "processing" / "dataset_25k.csv")

# Colonnes à nettoyer
cols = ['text', 'text_normalized']

# Fonction de nettoyage
def clean_text(column):
    column = column.astype(str)
    column = column.str.replace('\n', ' ')          # supprimer retour ligne
    column = column.str.strip('"')                  # supprimer guillemets externes
    column = column.str.strip()                     # supprimer espaces début/fin
    column = column.str.replace(r'\s+', ' ', regex=True)  # espaces multiples → 1 seul
    return column

# Appliquer sur les deux colonnes
for col in cols:
    df[col] = clean_text(df[col])

# Supprimer lignes vides (optionnel mais recommandé)
df = df[(df['text'].str.len() > 0) & (df['text_normalized'].str.len() > 0)]

# Sauvegarde
df.to_csv(HERE / "data" / "processing" / "dataset_25k_cleaned.csv", index=False)

print("Nettoyage terminé :", df.shape)