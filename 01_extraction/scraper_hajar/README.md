# 🇲🇦 Darija Dataset Scraper

Collecte automatisée de textes en Darija marocaine depuis YouTube (commentaires + transcriptions).

---

## 📁 Architecture du projet

```
darija_dataset/
├── config/
│   └── channels.yaml              ← CONFIGURATION PRINCIPALE
├── scrapers/
│   ├── youtube_comments.py        ← Scraping commentaires (YouTube Data API v3)
│   └── youtube_transcripts.py     ← Scraping transcriptions (youtube-transcript-api)
├── pipeline/
│   ├── runner.py                  ← Orchestrateur
│   └── exporter.py                ← Export CSV / JSON / stats
├── data/
│   ├── raw/                       ← Checkpoints par chaîne (auto-créé)
│   │   ├── religion/
│   │   ├── food/
│   │   ├── entertainment/
│   │   └── miscill/
│   └── final/
│       ├── dataset_final.csv      ← Dataset final (50 000 textes)
│       ├── dataset_final.json     ← Même dataset en JSON (pour Label Studio)
│       └── stats_report.txt       ← Rapport statistiques
├── logs/
│   └── scraping.log               ← Logs détaillés
├── main.py                        ← Point d'entrée
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

```bash
# 1. Cloner / copier le projet
cd darija_dataset

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
```

---

## 🔑 Configuration de l'API YouTube

1. Aller sur [Google Cloud Console](https://console.cloud.google.com)
2. Créer un projet → **APIs & Services** → **Library**
3. Chercher **YouTube Data API v3** → Activer
4. **Credentials** → **Create Credentials** → **API Key**
5. Copier la clé dans `config/channels.yaml` :

```yaml
api_key: "AIza..._clé_ici"
```

> **Quota** : L'API offre 10 000 unités/jour gratuitement.
> - 1 appel `search.list` = 100 unités
> - 1 appel `commentThreads.list` = 1 unité
> - Les transcriptions (`youtube-transcript-api`) **ne consomment pas de quota**.

---

## 🚀 Utilisation

```bash
# Vérifier la configuration (sans scraper)
python main.py --check-config

# Scraper TOUS les domaines (~50 000 textes)
python main.py

# Scraper un seul domaine
python main.py --domains religion

# Scraper plusieurs domaines
python main.py --domains food entertainment

# Domaines disponibles : religion, food, entertainment, miscill
```

---

## 📊 Format du dataset final

Le fichier `data/final/dataset_final.csv` contient les colonnes suivantes :

| Colonne          | Description                                          |
|------------------|------------------------------------------------------|
| `id`             | Identifiant unique (`darija_000001`)                 |
| `text`           | Texte brut en Darija (orthographe originale)         |
| `source_type`    | `youtube_comment` ou `youtube_transcript`            |
| `domain`         | Domaine thématique (`religion`, `food`, etc.)        |
| `channel_name`   | Nom lisible de la chaîne                             |
| `channel_handle` | Handle YouTube (@username)                           |
| `video_id`       | ID YouTube de la vidéo source                       |
| `video_title`    | Titre de la vidéo                                    |
| `published_at`   | Date de publication du commentaire/vidéo             |
| `label`          | Label initial (= domaine) → à valider/corriger       |
| `language`       | `darija`                                             |

---

## 📈 Estimation des textes par domaine

| Domaine       | Chaînes | Cible   |
|---------------|---------|---------|
| Religion      | 5       | ~12 500 |
| Food          | 6       | ~12 500 |
| Entertainment | 5       | ~12 500 |
| Miscill       | 2       | ~12 500 |
| **TOTAL**     | **18**  | **~50 000** |

---

## ⚠️ Gestion du quota API

Si vous atteignez le quota journalier (10 000 unités) :
- Le scraper s'arrête automatiquement et sauvegarde les checkpoints
- Relancer le lendemain avec `python main.py --domains <domaines_restants>`
- Les checkpoints par chaîne sont dans `data/raw/<domaine>/<handle>.csv`

---

## 🔄 Étapes suivantes (projet)

1. **Filtrage linguistique** : conserver uniquement les textes en Darija
2. **Annotation manuelle** : 1 000–2 000 textes gold standard
3. **Labellisation LLM** : pré-annotation via Claude/GPT
4. **Validation** : Label Studio
5. **Modélisation** : Logistic Regression, SVM, Naive Bayes
6. **Tracking** : MLflow ou W&B
