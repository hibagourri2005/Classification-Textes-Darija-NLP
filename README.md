# Classification automatique de textes en Darija marocaine

Constitution, annotation semi-automatique (LLM + validation humaine) et classification d'un corpus de
commentaires et transcriptions **YouTube / Instagram** en Darija. Projet réalisé en binôme (Hajar, Hiba) ;
cahier des charges : [`docs/cahier_des_charges.md`](docs/cahier_des_charges.md).

## Pipeline

```
01_extraction  ->  02_nettoyage_pretraitement  ->  03_labelisation  ->  04_modelisation
 scrapers          détecteur Darija, EDA,           Gemini (pré-annotation),     7 classifieurs x 5 représentations,
 YouTube/Insta     échantillon de 25 000 textes     Label Studio, contrôle        suivi Weights & Biases
                                                    qualité, équilibrage
```

| Dossier | Contenu |
|---|---|
| `01_extraction/scraper_hajar/` | Scraper YouTube (commentaires + transcriptions, `yt-dlp`) : `raw/` -> `final/` -> `merged/` |
| `01_extraction/scraper_hiba/` | Scrapers YouTube et Instagram (`scraping/`, résultats dans `data/raw/`) |
| `01_extraction/darija_statistics.ipynb` | Statistiques du corpus brut fusionné |
| `02_nettoyage_pretraitement/nettoyage/` | `darija_detector.py` + notebook de nettoyage (entrée : sortie de l'étape 1) |
| `02_nettoyage_pretraitement/pre_traitement/` | Échantillonnage des 25 000 textes, EDA, `clean_quotes.py` |
| `03_labelisation/etape1…etape4/` | Gold standard manuel, pré-annotation Gemini, vérification Label Studio, contrôle qualité |
| `04_modelisation/` | Notebooks de classification, figures, rapport HTML |
| `docs/` | Cahier des charges, rapport de modélisation, [`DONNEES.md`](docs/DONNEES.md), [`REORGANISATION.md`](docs/REORGANISATION.md) |

## Installation

```bash
python -m venv .venv && source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements.txt                        # étapes 2 et 3
pip install -r requirements-modelisation.txt           # étape 4 (torch, transformers, wandb…)
pip install -r requirements-scraping.txt               # étape 1 (scrapers)
```

## Exécution

> **Lancez chaque script / notebook depuis son propre dossier** : les chemins sont relatifs (`data/…`).

```bash
# Étape 1 : fusion des données scrapées (depuis 01_extraction/scraper_hajar/)
python merge_all.py && python merge_partners.py        # raw -> final -> merged

# Étape 2 : notebook darija_nettoyage.ipynb, puis (depuis pre_traitement/)
python code_extraire_25k.py && python verification.py && python nettoyage_basique.py

# Étape 3 : voir 03_labelisation/etape2_preannotation_llm/README.md
python extraire_batch.py                               # découpe en lots de 50 pour Gemini

# Étape 4 : 04_modelisation/Etape4_Classification_Darija_*.ipynb
```

Scrapers : copier `.env.example` en `.env` et renseigner vos identifiants (jamais dans le code).

## Résultats (modélisation)

Selon [`docs/rapport_modelisation_complet.md`](docs/rapport_modelisation_complet.md) : 47 802 commentaires, 12 classes ;
meilleur modèle individuel LinearSVC + TF-IDF caractères (F1-macro 0,604 / accuracy 0,634), meilleur ensemble
(Stacking) F1-macro 0,621 / accuracy 0,641. Deux notebooks coexistent : `ANNOTE` (31 mai, le plus récent) et
`FINAL_v4` (23 mai, correspond au rapport HTML).

## Données et éthique

Les fichiers volumineux ne sont pas versionnés (voir [`docs/DONNEES.md`](docs/DONNEES.md)). Les jeux de données ne
contiennent pas de pseudos d'auteurs, mais le texte des commentaires peut contenir des informations personnelles :
vérifiez les conditions d'utilisation des plateformes avant toute redistribution. Licence : à définir.
## Auteurs

Projet réalisé en groupe par :
- Hiba Gourri ([@hibagourri2005](https://github.com/hibagourri2005))
- Hajar Bellafrouh ([@Hajar-Bellafrouh](https://github.com/Hajar-Bellafrouh))

Dépôt d'origine : https://github.com/Hajar-Bellafrouh/classification-textes-darija