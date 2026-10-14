# 📁 Pipeline de Nettoyage et Comparaison CSV / JSON

Documentation complète des étapes de traitement des fichiers de données Darija.

---

## 🗂️ Vue d'ensemble

Ce pipeline permet de :
1. Supprimer du JSON les IDs absents du CSV
2. Trouver les IDs présents dans le CSV mais absents du JSON
3. Détecter et supprimer les doublons dans le JSON
4. Comparer les IDs entre les deux fichiers
5. Synchroniser le JSON sur le CSV

---

## Étape 1 — Supprimer du JSON les IDs absents du CSV

### 🎯 Objectif
Nettoyer le fichier JSON en supprimant toutes les entrées dont l'`id` n'existe pas dans le CSV.

### 📄 Script : `compare_and_clean.py`

```python
import csv
import json
import argparse
from pathlib import Path


def load_csv_ids(csv_path: str) -> set:
    """Charge tous les IDs depuis le fichier CSV."""
    ids = set()
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = ';' if sample.count(';') > sample.count(',') else ','
        reader = csv.DictReader(f, delimiter=delimiter)
        first_row = next(reader, None)
        if first_row is None:
            raise ValueError("Le fichier CSV est vide.")
        columns = list(first_row.keys())
        print(f"   → Colonnes détectées : {columns}")
        print(f"   → Séparateur utilisé : '{delimiter}'")
        if 'id' not in first_row:
            raise ValueError(f"Colonne 'id' introuvable. Colonnes disponibles : {columns}")
        ids.add(first_row['id'].strip())
        for row in reader:
            ids.add(row['id'].strip())
    return ids


def load_json(json_path: str) -> list:
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Le fichier JSON doit contenir une liste d'objets.")
    return data


def compare_and_clean(csv_path, json_path, output_path=None):
    csv_ids = load_csv_ids(csv_path)
    json_data = load_json(json_path)

    cleaned_data = []
    removed = []

    for entry in json_data:
        entry_id = str(entry.get('id', '')).strip()
        if entry_id in csv_ids:
            cleaned_data.append(entry)
        else:
            removed.append(entry_id)

    if output_path is None:
        p = Path(json_path)
        output_path = str(p.parent / (p.stem + "_cleaned" + p.suffix))

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

    return cleaned_data, removed
```

### ▶️ Commande
```bash
python compare_and_clean.py dataset_total_clean.csv mon_data.json
```

### ✅ Résultat obtenu
```
📂 Chargement du CSV  : dataset_total_clean.csv
   → Colonnes détectées : ['id', 'text', 'text_normalized', ...]
   → Séparateur utilisé : ','
   → 25001 IDs trouvés dans le CSV
📂 Chargement du JSON : mon_data.json
   → 25005 entrées trouvées dans le JSON

📊 Résultats :
   ✅ Entrées conservées : 25001
   ❌ Entrées supprimées : 4

💾 Fichier JSON nettoyé sauvegardé : mon_data_cleaned.json
```

---

## Étape 2 — Trouver les IDs manquants dans le JSON

### 🎯 Objectif
Identifier les IDs présents dans le CSV mais absents du JSON, et les exporter dans un nouveau fichier JSON avec les colonnes `id`, `text_normalized`, `domain`, `label`.

### 📄 Script : `find_missing_ids.py`

```python
import csv
import json
import argparse
from pathlib import Path


def load_csv(csv_path: str) -> dict:
    rows = {}
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = ';' if sample.count(';') > sample.count(',') else ','
        reader = csv.DictReader(f, delimiter=delimiter)
        first_row = next(reader, None)
        rows[first_row['id'].strip()] = first_row
        for row in reader:
            rows[row['id'].strip()] = row
    return rows


def load_json_ids(json_path: str) -> set:
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    return {str(entry.get('id', '')).strip() for entry in data}


def find_missing(csv_path, json_path, output_path=None):
    csv_data = load_csv(csv_path)
    json_ids = load_json_ids(json_path)

    missing_ids = set(csv_data.keys()) - json_ids

    output = []
    for mid in sorted(missing_ids):
        row = csv_data[mid]
        output.append({
            "id": mid,
            "text_normalized": row.get("text_normalized", "").strip(),
            "domain": row.get("domain", "").strip() or None,
            "label": row.get("label", None) or None
        })

    if output_path is None:
        output_path = "missing_ids.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return output
```

### ▶️ Commande
```bash
python find_missing_ids.py dataset_total_clean.csv mon_data.json
```

### ✅ Résultat obtenu
```
📂 Chargement du CSV  : dataset_total_clean.csv
   → 25001 entrées trouvées dans le CSV

📂 Chargement du JSON : mon_data.json
   → 25003 IDs trouvés dans le JSON

📊 Résultats :
   ✅ IDs en commun         : 25001
   ❌ IDs manquants dans JSON: 0

💾 Fichier sauvegardé : missing_ids.json
```

### 📦 Format du fichier de sortie `missing_ids.json`
```json
[
  {
    "id": "darija_050244",
    "text_normalized": "واش ملي نعمروهم في البواطة نعمل في الكنجلاطور كتبقا مزيانة",
    "domain": "food",
    "label": null
  }
]
```

---

## Étape 3 — Détecter les doublons dans le JSON

### 🎯 Objectif
Vérifier si des entrées ont le même `id` dans le fichier JSON et afficher un rapport détaillé.

### 📄 Script : `check_duplicates.py`

```python
import json
from collections import Counter


def check_duplicates(json_path: str, output_path: str = None):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    id_counts = Counter(str(entry.get('id', '')).strip() for entry in data)
    duplicates = {id_: count for id_, count in id_counts.items() if count > 1}

    print(f"📊 Résultats :")
    print(f"   🔢 Total entrées       : {len(data)}")
    print(f"   ✅ IDs uniques         : {len(id_counts)}")
    print(f"   ❌ IDs en doublon      : {len(duplicates)}")

    if output_path:
        seen = set()
        deduped = [e for e in data if not (str(e.get('id','')).strip() in seen or seen.add(str(e.get('id','')).strip()))]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(deduped, f, ensure_ascii=False, indent=2)
```

### ▶️ Commande
```bash
python check_duplicates.py mon_data.json
```

### ✅ Résultat obtenu
```
📂 Chargement du JSON : mon_data.json
   → 25005 entrées trouvées

📊 Résultats :
   🔢 Total entrées       : 25005
   ✅ IDs uniques         : 25003
   ❌ IDs en doublon      : 2
   ♻️  Entrées redondantes : 2

🗂️  Détail des doublons :
   ID                             Occurrences
   ------------------------------ ----------
   darija_079393                           2
   darija_116937                           2
```

---

## Étape 4 — Supprimer les doublons

### 🎯 Objectif
Supprimer les entrées dupliquées du JSON en gardant uniquement la première occurrence de chaque `id`.

### 📄 Script : `remove_duplicates.py`

```python
import json


def remove_duplicates(json_path: str, output_path: str = None):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    seen = set()
    deduped = []
    removed = []

    for entry in data:
        eid = str(entry.get('id', '')).strip()
        if eid not in seen:
            seen.add(eid)
            deduped.append(entry)
        else:
            removed.append(eid)

    if output_path is None:
        output_path = json_path  # Écraser le fichier original

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)

    return deduped, removed
```

### ▶️ Commande
```bash
python remove_duplicates.py mon_data.json --output mon_data_clean.json
```

### ✅ Résultat obtenu
```
📂 Chargement du JSON : mon_data.json
   → 25005 entrées avant déduplication

📊 Résultats :
   ✅ Entrées conservées : 25003
   ❌ Doublons supprimés : 2

🗑️  IDs dédupliqués :
   - darija_079393
   - darija_116937

💾 Fichier sauvegardé : mon_data_clean.json
```

---

## Étape 5 — Comparer les IDs entre CSV et JSON

### 🎯 Objectif
Vérifier si les deux fichiers contiennent exactement les mêmes IDs, et identifier les divergences.

### 📄 Script : `compare_ids.py`

```python
import csv
import json


def compare_ids(csv_path: str, json_path: str):
    # Charger les IDs du CSV
    csv_ids = set()
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        sample = f.read(2048); f.seek(0)
        delimiter = ';' if sample.count(';') > sample.count(',') else ','
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            csv_ids.add(row['id'].strip())

    # Charger les IDs du JSON
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    json_ids = {str(e.get('id', '')).strip() for e in data}

    common       = csv_ids & json_ids
    only_in_csv  = csv_ids - json_ids
    only_in_json = json_ids - csv_ids

    print(f"  ✅ IDs en commun               : {len(common)}")
    print(f"  📄 IDs uniquement dans le CSV  : {len(only_in_csv)}")
    print(f"  📋 IDs uniquement dans le JSON : {len(only_in_json)}")
```

### ▶️ Commande
```bash
python compare_ids.py dataset_total_clean.csv mon_data_clean.json
```

### ✅ Résultat obtenu
```
📂 Chargement du CSV  : dataset_total_clean.csv
   → 25001 IDs uniques dans le CSV
📂 Chargement du JSON : mon_data_clean.json
   → 25003 IDs uniques dans le JSON

==================================================
📊 RÉSUMÉ DE LA COMPARAISON
==================================================
  ✅ IDs en commun (dans les deux)  : 25001
  📄 IDs uniquement dans le CSV     : 0
  📋 IDs uniquement dans le JSON    : 2

⚠️  Les fichiers ne sont PAS identiques.

📋 IDs présents dans JSON mais absents du CSV (2) :
   - darija_06715
   - darija_08476
```

---

## Étape 6 — Synchroniser le JSON sur le CSV

### 🎯 Objectif
Supprimer du JSON les IDs qui ne sont pas dans le CSV pour que les deux fichiers soient parfaitement synchronisés.

### 📄 Script : `sync_json_to_csv.py`

```python
import csv
import json


def sync_json_to_csv(csv_path: str, json_path: str, output_path: str = None):
    # Charger les IDs du CSV
    csv_ids = set()
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        sample = f.read(2048); f.seek(0)
        delimiter = ';' if sample.count(';') > sample.count(',') else ','
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            csv_ids.add(row['id'].strip())

    # Charger le JSON
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    # Filtrer
    cleaned = [e for e in data if str(e.get('id', '')).strip() in csv_ids]
    removed = [str(e.get('id', '')).strip() for e in data
               if str(e.get('id', '')).strip() not in csv_ids]

    if output_path is None:
        output_path = json_path

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    return cleaned, removed
```

### ▶️ Commande
```bash
python sync_json_to_csv.py dataset_total_clean.csv mon_data_clean.json
```

### ✅ Résultat obtenu
```
📂 Chargement du CSV  : dataset_total_clean.csv
   → 25001 IDs dans le CSV
📂 Chargement du JSON : mon_data_clean.json
   → 25003 entrées dans le JSON

📊 Résultats :
   ✅ Entrées conservées : 25001
   ❌ Entrées supprimées : 2

🗑️  IDs supprimés :
   - darija_06715
   - darija_08476

💾 Fichier sauvegardé : mon_data_clean.json
   → JSON et CSV contiennent maintenant les mêmes 25001 IDs ✅
```

---

## 🔁 Résumé du Pipeline

```
dataset_total_clean.csv
        │
        ▼
[Étape 1] compare_and_clean.py     → Supprime du JSON les IDs absents du CSV
        │
        ▼
[Étape 2] find_missing_ids.py      → Exporte les IDs CSV absents du JSON
        │
        ▼
[Étape 3] check_duplicates.py      → Détecte les doublons dans le JSON
        │
        ▼
[Étape 4] remove_duplicates.py     → Supprime les doublons (garde 1ère occurrence)
        │
        ▼
[Étape 5] compare_ids.py           → Vérifie la cohérence CSV ↔ JSON
        │
        ▼
[Étape 6] sync_json_to_csv.py      → Synchronisation finale JSON = CSV
        │
        ▼
   mon_data_final.json ✅
   (25001 entrées uniques, synchronisées avec le CSV)
```

---

## 📊 Statistiques finales

| Étape | Avant | Après | Différence |
|-------|-------|-------|------------|
| Nettoyage initial (Étape 1) | 25005 entrées JSON | 25001 | -4 supprimées |
| Déduplication (Étape 4) | 25005 entrées JSON | 25003 | -2 doublons |
| Synchronisation finale (Étape 6) | 25003 entrées JSON | 25001 | -2 hors CSV |
| **Résultat final** | — | **25001** | **CSV = JSON ✅** |
