# Données

## Jeux de données principaux (versionnés)

| Fichier | Lignes | Colonnes / remarque |
|---|---|---|
| `03_labelisation/etape4_controle_qualite/dataset_darija_25k_text_only.csv` | 25 000 | `id, text, label, domain` |
| `03_labelisation/etape4_controle_qualite/dataset_darija_final_25k.csv` | 17 003 | `id, text, label, domain` (équilibré par classe) |
| `03_labelisation/etape1_annotation_manuelle/gold_standard/dataset_annotated.csv` | 1 007 | gold standard manuel |
| `02_nettoyage_pretraitement/pre_traitement/data/final/dataset_total_clean.csv` | 25 001 | 21 colonnes (script, score détecteur, code-switching…) |
| `04_modelisation/Dataset_Final.csv` | 47 802 | `id, text, source_platform, source_type, source_account, category, date, label, script` : entrée de la modélisation |

## Fichiers volumineux non versionnés (`.gitignore`)

Présents dans le zip fourni, mais exclus de Git (limite GitHub : 100 Mo/fichier). À partager via Git LFS, Zenodo, Hugging Face ou Drive.

| Fichier | Taille | Régénération |
|---|---|---|
| `scraper_hajar/data/final/dataset_final.{csv,json}` | 29 / 56 Mo | `python merge_all.py` |
| `scraper_hajar/data/merged/dataset_merged.{csv,json}` | 36 / 64 Mo | `python merge_partners.py` |
| `scraper_hajar/data/partner/youtube_raw.csv` | 20 Mo | données du binôme (Hiba) |
| `scraper_hiba/data/raw/youtube_raw.json` | 33 Mo | `scraping/youtube_scraper.py` |
| `nettoyage/data/processed/darija_clean.{csv,json}` | 24 / 53 Mo | notebook `darija_nettoyage.ipynb` |
| `pre_traitement/data/processing/dataset_rest.csv` | 16 Mo | `code_extraire_25k.py` |
| `etape2…/llm_batches/` (501 fichiers) | 5 Mo | `extraire_batch.py` |
| `etape2…/Gemini_Chats_Export/` (502 fichiers) | 4 Mo | sorties brutes de Gemini (non régénérables) |
| `04_modelisation/wandb/`, `*.npy` | 2 / 12 Mo | contiennent des chemins locaux de la machine ; `wandb sync` possible |
