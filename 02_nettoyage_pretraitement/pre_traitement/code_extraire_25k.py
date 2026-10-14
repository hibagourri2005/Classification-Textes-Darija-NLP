import pandas as pd
from pathlib import Path
HERE = Path(__file__).resolve().parent

# 1. Charger le dataset
df = pd.read_csv(HERE / ".." / "nettoyage" / "data" / "processed" / "darija_clean.csv")  # sortie du notebook de nettoyage

# Vérifier les labels
print(df['label'].value_counts())

# 2. Nombre souhaité par domaine
samples_per_label = {
    "medical": 1189,
    "miscill": 1466,
    "religion": 1519,
    "politics": 3145,
    "sports": 4026,
    "business": 4458,
    "food": 4500,
    "entertainment": 4700
}

# 3. Sampling contrôlé
df_25k = pd.DataFrame()

for label, n in samples_per_label.items():
    subset = df[df['label'] == label]
    
    # Vérification importante
    if len(subset) < n:
        print(f"⚠️ Attention: {label} contient seulement {len(subset)} lignes (demandé: {n})")
        sampled = subset  # prendre tout si insuffisant
    else:
        sampled = subset.sample(n=n, random_state=42)
    
    df_25k = pd.concat([df_25k, sampled])

# 4. Mélanger le dataset final (optionnel mais recommandé)
df_25k = df_25k.sample(frac=1, random_state=42).reset_index(drop=True)

# 5. Le reste
df_rest = df.drop(df_25k.index)

# 6. Sauvegarde
(HERE / "data" / "processing").mkdir(parents=True, exist_ok=True)
df_25k.to_csv(HERE / "data" / "processing" / "dataset_25k.csv", index=False)
df_rest.to_csv(HERE / "data" / "processing" / "dataset_rest.csv", index=False)

# 7. Vérification
print("\nDistribution finale (25k) :")
print(df_25k['label'].value_counts())

print("\nTailles :")
print("Dataset 25k :", df_25k.shape)
print("Dataset rest :", df_rest.shape)