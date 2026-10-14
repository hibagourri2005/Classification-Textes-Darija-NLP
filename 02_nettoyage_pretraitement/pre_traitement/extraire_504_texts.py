import pandas as pd
from pathlib import Path
HERE = Path(__file__).resolve().parent

# 1. Charger les données
df = pd.read_csv(HERE / "data" / "processing" / "dataset_25k_cleaned.csv")

# 2. Vérifier les domaines
domains = df['domain'].unique()
print("Domains :", domains)

# 3. Initialisation
df_file1 = pd.DataFrame()
df_file2 = pd.DataFrame()

# 4. Boucle sur chaque domaine
for domain in domains:
    subset = df[df['domain'] == domain]

    # Vérifier qu'on a assez de données
    if len(subset) < 126:
        raise ValueError(f"Pas assez de données pour le domaine {domain}")

    # Mélanger les données
    subset = subset.sample(frac=1, random_state=42)

    # 63 pour fichier 1
    part1 = subset.iloc[:63]

    # 63 pour fichier 2
    part2 = subset.iloc[63:126]

    # Ajouter aux datasets
    df_file1 = pd.concat([df_file1, part1])
    df_file2 = pd.concat([df_file2, part2])

# 5. Supprimer les données utilisées
used_indices = pd.concat([df_file1, df_file2]).index
df_rest = df.drop(used_indices)

# 6. Supprimer l'ancienne colonne label si elle existe
if 'label' in df_file1.columns:
    df_file1 = df_file1.drop(columns=['label'])
    df_file2 = df_file2.drop(columns=['label'])
    df_rest = df_rest.drop(columns=['label'])

# 7. Ajouter une colonne label vide à la fin
df_file1['label'] = ""
df_file2['label'] = ""
df_rest['label'] = ""

# 8. Sauvegarde
(HERE / "data" / "extraire1000").mkdir(parents=True, exist_ok=True)
df_file1.to_csv(HERE / "data" / "extraire1000" / "fichier1_504.csv", index=False)
df_file2.to_csv(HERE / "data" / "extraire1000" / "fichier2_504.csv", index=False)
df_rest.to_csv(HERE / "data" / "extraire1000" / "fichier_reste.csv", index=False)

# 9. Vérification
print("Fichier1 :", df_file1.shape)
print(df_file1['domain'].value_counts())

print("\nFichier2 :", df_file2.shape)
print(df_file2['domain'].value_counts())

print("\nReste :", df_rest.shape)