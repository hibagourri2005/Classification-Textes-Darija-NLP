"""
count_texts.py
Affiche le total de textes scrapés par domaine et par chaîne.
Lance : python count_texts.py
"""

import pandas as pd
import glob
from pathlib import Path

RAW_DIR = Path("data/raw")

all_files = glob.glob(str(RAW_DIR / "**" / "*.csv"), recursive=True)

if not all_files:
    print("❌ Aucune donnée trouvée dans data/raw/")
    print("   Lance d'abord : python main.py --domains <domaine>")
    exit()

# Organiser par domaine
domains = {}
for f in sorted(all_files):
    path = Path(f)
    domain = path.parent.name
    try:
        df = pd.read_csv(f)
        n = len(df)
    except Exception:
        n = 0
    if domain not in domains:
        domains[domain] = []
    domains[domain].append({"file": path.name, "count": n})

# Affichage
print("\n" + "=" * 55)
print("  TEXTES SCRAPÉS PAR DOMAINE")
print("=" * 55)

grand_total = 0
for domain, files in sorted(domains.items()):
    domain_total = sum(f["count"] for f in files)
    grand_total += domain_total
    status = "✅" if domain_total > 1000 else "⚠️ " if domain_total > 0 else "❌"
    print(f"\n  {status} {domain.upper():20s} → {domain_total:6d} textes")
    for f in files:
        bar = "█" * min(30, f["count"] // 100)
        print(f"     • {f['file'].replace('.csv',''):30s} {f['count']:5d}  {bar}")

print("\n" + "=" * 55)
print(f"  TOTAL GÉNÉRAL : {grand_total} textes")
print("=" * 55)

# Domaines manquants
all_domains = ["religion", "food", "entertainment", "miscill",
               "medical", "business", "sports", "politics"]
done = list(domains.keys())
missing = [d for d in all_domains if d not in done]
if missing:
    print(f"\n  ⏳ Domaines pas encore scrapés : {', '.join(missing)}")
else:
    print(f"\n  🎉 Tous les domaines sont scrapés !")
    print(f"  → Lance maintenant : python merge_all.py")
print()