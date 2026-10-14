import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Remplace par le chemin de ton fichier CSV
csv_file = Path(__file__).resolve().parent / "data" / "processed" / "darija_clean.csv"

# Chargement du fichier
df = pd.read_csv(csv_file)

# Distribution par domaine
distribution = df["domain"].value_counts()

print("\nDistribution après nettoyage :")
print(distribution)

# Affichage graphique
plt.figure(figsize=(8, 5))
distribution.plot(kind="bar")
plt.title("Distribution des domaines après nettoyage")
plt.xlabel("Domaine")
plt.ylabel("Nombre de textes")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()