import pandas as pd
import os
from pathlib import Path
HERE = Path(__file__).resolve().parent

# 1. Charger le dataset
df = pd.read_csv(HERE / "data" / "initial_unannotated" / "dataset_total_clean.csv")

# 2. Garder uniquement les colonnes utiles
columns_to_keep = [
    "id",
    "text_normalized",
    "domain",
    "label"
]

df = df[columns_to_keep]

# 3. Vérification
print("Colonnes utilisées :", df.columns)

# 4. Créer dossier de sortie
output_folder = str(HERE / "llm_batches")
os.makedirs(output_folder, exist_ok=True)

# 5. Découpage en fichiers de 200 lignes
rows_per_file = 50

for i, start in enumerate(range(0, len(df), rows_per_file)):
    chunk_df = df.iloc[start:start + rows_per_file]

    file_path = os.path.join(output_folder, f"batch_{i}.json")

    chunk_df.to_json(
        file_path,
        orient="records",
        indent=2,
        force_ascii=False
    )

    print(f"Saved {file_path}")

print("Découpage terminé !")