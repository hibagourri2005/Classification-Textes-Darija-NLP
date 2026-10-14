# Changements apportés lors de la réorganisation

## Sécurité
Des identifiants en clair ont été retirés du code (clé RapidAPI dans `debug_api.py` et `find_endpoints.py` ; login et mot de
passe Instagram dans `instagram_scraper.py`). Ils sont désormais lus dans `.env` (voir `.env.example`).
**Ces identifiants ont été partagés : changez le mot de passe Instagram et régénérez la clé RapidAPI.**

## Dossiers renommés
`Scraping_Hiba` -> `scraper_hiba` ; `scrapping_hajar/darija_dataset` -> `scraper_hajar` ; `pre-traitement` -> `pre_traitement` ;
`Étape N – …` -> `etapeN_…` ; `vrai_modelisation` -> `04_modelisation`. Dans le scraper de Hajar, `raw_1/merged_1/merged_2/raw_2`
sont redevenus `raw/final/merged/partner` (noms attendus par `runner.py`, `merge_all.py`, `merge_partners.py`).

## Liens corrigés
- `darija_nettoyage.ipynb` : lit `../../01_extraction/scraper_hajar/data/merged/dataset_merged.csv` et `darija_detector.py` (ex `Darija detector.py`).
- `code_extraire_25k.py`, `verification.py`, `nettoyage_basique.py`, `extraire_504_texts.py` : chemins `data/processing/…` (l'ancien `../25k/…` n'existait pas).
- `clean.py` -> `clean_quotes.py` : fichiers d'entrée/sortie en arguments (les noms codés en dur n'existaient pas).
- `extraire_batch.py` : `data/initial_unannotated/…` ; `merge_partners.py` : fichier partenaire par défaut `data/partner/youtube_raw.csv`.
- Étape 3 : `enfin/` -> `data_final/` ; `data_verifié_auto.json` -> `data_verifie_auto.json`.
- `partie_4.ipynb` : variable `corrections` jamais définie (cellule supprimée), ajoutée.
- `darija_statistics.ipynb` et `EDA_Darija_25k.ipynb` : chemins Windows `\` -> `/`.

## Doublons supprimés (hash identique, vérifié)
7 copies exactes (~254 Mo) : `dataset_merged.{csv,json}` (x3), `darija_clean.csv` (x2), `youtube_raw.json`, `Darija detector.py`.
Le dossier `nouveau/` a été dissous (relance plus récente du même notebook ; l'ancienne est dans `_archive/`).

## Vérifications effectuées
`raw -> final -> merged` rejoué : 123 717 et 175 857 lignes, textes identiques. Les 501 lots LLM sont régénérés à l'identique.
Notebooks exécutés avec succès : statistiques, EDA, étape 3, `partie_4`. Non exécutés (torch/BERT/wandb) : notebooks de modélisation,
et nettoyage (long).

## Points à vérifier par l'équipe
- `code_extraire_25k.py` régénère 25 003 textes ; le fichier livré en compte 25 001 (2 retirés à la main, étape non scriptée).
- Le `fichier_reste.csv` livré (25 001 lignes) ne correspond pas à la sortie de `extraire_504_texts.py` (23 995).
