# ⚡ Guide — Collecte en 2-3 jours (50 000 textes)

## Plan recommandé

| Jour | Commande | Domaines | Textes estimés |
|------|----------|----------|----------------|
| Jour 1 matin | `python main.py --domains religion food` | Religion + Food | ~25 000 |
| Jour 1 soir | Vérifier `data/raw/` — checkpoints OK ? | — | — |
| Jour 2 matin | `python main.py --domains entertainment miscill` | Entertain. + Miscill | ~25 000 |
| Jour 2 soir | Dataset final prêt dans `data/final/` | — | ~50 000 |

> Si interruption → relancer la même commande, les checkpoints sont sauvegardés par chaîne.

---

## Installation (une seule fois)

```bash
pip install -r requirements.txt
python main.py --check-config   # vérifier que yt-dlp est OK
```

---

## Commandes utiles

```bash
# Lancer tout d'un coup (si connexion stable, toute une nuit)
python main.py

# Domaine par domaine (recommandé)
python main.py --domains religion
python main.py --domains food
python main.py --domains entertainment
python main.py --domains miscill

# Voir la progression en temps réel
tail -f logs/scraping.log

# Compter les textes déjà collectés
python -c "
import pandas as pd, glob
files = glob.glob('data/raw/**/*.csv', recursive=True)
total = sum(len(pd.read_csv(f)) for f in files)
print(f'Textes collectés jusqu\\'à présent : {total}')
for f in files:
    df = pd.read_csv(f)
    print(f'  {f}: {len(df)} textes')
"
```

---

## Si YouTube ralentit ou bloque

```bash
# Augmenter le sleep dans config/channels.yaml :
# sleep_between_requests: 2.0   (au lieu de 1.0)
# max_workers: 2                (au lieu de 3)

# Attendre 1-2h puis relancer
python main.py --domains <domaine_interrompu>
```

---

## Structure du dataset final

```
data/final/dataset_final.csv   ← dataset prêt pour annotation
data/final/dataset_final.json  ← même données pour Label Studio
data/final/stats_report.txt    ← statistiques complètes
data/raw/<domaine>/<handle>.csv ← checkpoints par chaîne
logs/scraping.log               ← log détaillé
```

## Colonnes du CSV

| Colonne | Exemple |
|---------|---------|
| id | darija_000001 |
| text | واش هاد الوصفة زوينة؟ بغيت نجربها |
| source_type | youtube_comment / youtube_transcript |
| domain | food |
| channel_name | Cuisine Tima |
| video_id | dQw4w9WgXcQ |
| label | food (à valider manuellement) |
| language | darija |
