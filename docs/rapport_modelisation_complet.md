# Étape 4 — Classification de Texte en Darija Marocaine
## Rapport Complet & Détaillé — Pipeline NLP de A à Z

> **Pour qui ?** Ce rapport explique **de zéro**, étape par étape, tout ce qui a été réalisé dans l'Étape 4 du projet. Il est conçu pour être intégré dans le rapport final et pour permettre à toute l'équipe d'expliquer cette partie avec précision.

---

## 📋 Table des Matières

| # | Section | Contenu |
|---|---------|---------|
| 1 | [Vue d'ensemble du projet](#1-vue-densemble-du-projet) | Objectif, dataset, plan |
| 2 | [Glossaire des mots-clés](#2-glossaire-des-mots-clés) | Définitions essentielles |
| 3 | [Importation des bibliothèques](#3-section-1--importation-des-bibliothèques) | Outils utilisés |
| 4 | [Exploration des données (EDA)](#4-section-2--exploration-des-données-eda) | Comprendre le dataset |
| 5 | [Prétraitement Darija](#5-section-3--prétraitement-spécialisé-darija) | Nettoyage des textes |
| 6 | [Séparation Train / Test](#6-section-4--séparation-train--test) | Découpe des données |
| 7 | [Vectorisation](#7-section-5--vectorisation-transformer-les-textes-en-nombres) | TF-IDF, BoW, n-grams |
| 8 | [Définition des modèles](#8-section-6--définition-des-modèles-de-classification) | 7 algorithmes |
| 9 | [Benchmark 35 combinaisons](#9-section-7--benchmark-systématique--35-combinaisons) | Comparaison exhaustive |
| 10 | [Analyse du meilleur modèle](#10-section-8--analyse-approfondie-du-meilleur-modèle) | Rapport + matrice de confusion |
| 11 | [Méthodes d'ensemble](#11-section-9--méthodes-densemble) | Voting, Stacking |
| 12 | [Optimisation des hyperparamètres](#12-section-10--optimisation-des-hyperparamètres) | GridSearch |
| 13 | [Courbes d'apprentissage](#13-section-11--courbes-dapprentissage) | Diagnostic overfitting |
| 14 | [WordClouds](#14-section-12--wordclouds-par-classe) | Visualisation vocabulaire |
| 15 | [Visualisation t-SNE](#15-section-13--visualisation-t-sne) | Réduction de dimension |
| 16 | [Calibration et confiance](#16-section-14--calibration-et-confiance-du-modèle) | Probabilités et seuils |
| 17 | [Features discriminantes](#17-section-15--features-les-plus-discriminantes) | Interprétabilité |
| 18 | [Tableau de bord final](#18-section-16--tableau-de-bord-final-dashboard) | Dashboard synthèse |
| 19 | [Prédiction interactive](#19-section-17--fonction-de-prédiction-interactive) | Prototype de service |
| 20 | [Cross-Validation 5 plis](#20-section-18--cross-validation-5-plis) | Évaluation robuste |
| 21 | [FastText Embeddings](#21-section-19--fasttext-embeddings--svm-hybride) | Embeddings denses |
| 22 | [DarijaBERT](#22-section-20--darijabert--cls-embeddings) | Modèle BERT spécialisé |
| 23 | [Tableau récapitulatif final](#23-section-21--tableau-récapitulatif-complet-toutes-expériences) | Toutes les expériences |
| 24 | [Suivi W&B](#24-section-22--suivi-expérimental-avec-weights--biases) | MLOps & tracking |
| 25 | [Analyses complémentaires](#25-section-23--analyses-complémentaires) | Source, longueur, BERT guide |
| 26 | [Rapport HTML](#26-section-24--rapport-html-exportable) | Export automatique |
| 27 | [Synthèse & Conclusions](#27-section-25--synthèse-et-conclusions-générales) | Bilan global |

---

## 1. Vue d'ensemble du projet

### Objectif principal
L'Étape 4 consiste à construire un **système de classification automatique** capable de lire un commentaire en Darija marocaine et de lui attribuer automatiquement une des **12 catégories thématiques** (Sport, Religion, Nourriture, Politique, etc.).

### Le dataset
- **47 802 commentaires YouTube** en Darija marocaine
- **12 classes** thématiques annotées manuellement
- **4 scripts d'écriture** coexistent : arabe (اَلْعَرَبِيَّةُ), latin (abc), mixte, autre
- Séparation : **80% entraînement** (38 241 exemples) / **20% test** (9 561 exemples)

### Défi spécifique : pourquoi la Darija est difficile
La Darija marocaine est une **langue peu dotée** (Low-Resource Language) pour plusieurs raisons :
- Elle **mélange** l'arabe classique, le français, l'amazigh et l'espagnol dans une même phrase
- Elle n'a **pas d'orthographe standardisée** : "mezyan", "mzyan", "mzien" représentent le même mot
- Elle utilise **deux systèmes d'écriture** : arabe et latin (translittération phonétique)
- Il existe **très peu de ressources NLP** pour cette langue comparé à l'anglais ou le français

### Résumé des performances obtenues

| Approche | F1-macro | Accuracy |
|----------|----------|----------|
| Meilleur modèle individuel (Linear SVC + TF-IDF char) | 0.604 | 0.634 |
| Meilleur ensemble (Stacking) | 0.621 | 0.641 |
| Hybride TF-IDF + FastText | 0.610 | 0.637 |
| TF-IDF + DarijaBERT (4k exemples) | 0.552 | 0.563 |

---

## 2. Glossaire des mots-clés

Avant de plonger dans les détails techniques, voici les définitions des termes les plus importants que vous devrez maîtriser pour expliquer ce projet.

| Terme | Définition simple |
|-------|-------------------|
| **Darija** | Le dialecte arabe marocain — mélange d'arabe, français, amazigh et espagnol |
| **NLP** | Natural Language Processing = traitement automatique du langage par ordinateur |
| **Classification** | Tâche de ranger automatiquement un texte dans une catégorie prédéfinie |
| **TF-IDF** | Méthode pour transformer un texte en vecteur de nombres en donnant plus de poids aux mots rares |
| **N-gram** | Séquence de N mots ou caractères consécutifs — ex. bigramme = 2 mots à la suite |
| **Vectorisation** | Conversion d'un texte (mots) en vecteur de nombres pour que l'algorithme puisse calculer |
| **F1-macro** | Métrique principale : moyenne du score F1 sur toutes les classes, sans favoriser les classes majoritaires |
| **Accuracy** | Pourcentage de textes bien classés — trompeuse sur données déséquilibrées |
| **Overfit / Surapprentissage** | Quand le modèle mémorise les données d'entraînement mais ne généralise pas sur de nouveaux textes |
| **Cross-validation** | Technique d'évaluation robuste qui répète l'entraînement sur 5 sous-ensembles différents |
| **BERT / DarijaBERT** | Modèle de langage très puissant pré-entraîné spécifiquement sur la Darija marocaine |
| **FastText** | Modèle d'embeddings qui représente les mots par des vecteurs denses (100 nombres réels) |
| **Stacking** | Technique d'ensemble où les prédictions de plusieurs modèles alimentent un méta-classifieur |
| **Hyperparamètre** | Réglage choisi avant l'entraînement (ex. taux d'apprentissage, C de régularisation) |
| **Matrice de confusion** | Tableau croisant les vraies classes et les classes prédites — révèle les erreurs du modèle |
| **t-SNE** | Algorithme de visualisation qui projette des données de haute dimension en 2D |
| **Recall** | Taux de détection : sur 100 vrais "Sport", combien ont été retrouvés ? |
| **Précision** | Qualité des prédictions : sur 100 prédits "Sport", combien le sont vraiment ? |
| **Code-switching** | Phénomène linguistique où le locuteur alterne plusieurs langues dans la même phrase |
| **Matrice creuse (sparse)** | Matrice avec une très grande majorité de valeurs nulles — TF-IDF en est un exemple |
| **Embeddings** | Représentation vectorielle dense d'un mot dans un espace de haute dimension |

---

## 3. Section 1 — Importation des Bibliothèques

### Qu'est-ce qu'on fait ici ?
Avant de pouvoir travailler, on doit **charger tous les outils** qu'on va utiliser. C'est comme préparer son matériel avant de commencer une expérience scientifique. En Python, ces outils s'appellent des **bibliothèques** (ou modules/packages).

### Rôle de chaque bibliothèque

| Bibliothèque | Rôle | Analogie |
|-------------|------|----------|
| `pandas` | Manipuler les tableaux de données (comme Excel) | Un tableur Excel intelligent |
| `numpy` | Calculs mathématiques sur des tableaux de nombres | Une calculatrice scientifique |
| `matplotlib / seaborn` | Dessiner des graphiques et visualisations | Un logiciel de dessin |
| `sklearn` | Tous les algorithmes de machine learning | Une boîte à outils ML complète |
| `gensim` | Entraîner des modèles FastText sur nos données | Un spécialiste des embeddings de mots |
| `scipy.sparse` | Gérer les matrices très grandes avec peu de données non-nulles | Compression intelligente |
| `wandb` | Suivre et enregistrer toutes nos expériences | Un carnet de laboratoire numérique |

### Concepts-clés du code

- **`np.random.seed(42)`** : Fixe une graine aléatoire → garantit que les résultats sont **reproductibles** (même résultat à chaque exécution). Le 42 est une constante arbitraire, choisie par convention dans la communauté ML.
- **`SEED = 42`** : Constante réutilisée partout dans le notebook pour la reproductibilité.
- **`warnings.filterwarnings("ignore")`** : Cache les avertissements non critiques pour garder la sortie propre.
- **`plt.rcParams.update(...)`** : Configure le style global de tous les graphiques (résolution DPI=120, couleurs, polices).

### Pourquoi la reproductibilité est-elle importante ?
Sans graine aléatoire fixe, chaque exécution du notebook pourrait donner des résultats légèrement différents (à cause des initialisations aléatoires des algorithmes). Avec `seed=42`, n'importe qui peut exécuter le code et obtenir exactement les mêmes résultats — c'est une exigence fondamentale en recherche scientifique.

---

## 4. Section 2 — Exploration des Données (EDA)

### Qu'est-ce que l'EDA ?
**EDA = Exploratory Data Analysis** (Analyse Exploratoire des Données).

> **Analogie :** Avant de cuisiner, vous inspectez vos ingrédients — combien en avez-vous, sont-ils frais, y en a-t-il assez de chaque type ? L'EDA fait pareil avec les données.

Avant de construire un modèle, il faut **comprendre les données** : combien d'exemples, quelles classes, des déséquilibres ? Des données mal comprises donnent des modèles mal entraînés.

### Structure du dataset

```
Colonnes : ['text', 'label', 'script', 'source_type', ...]
Exemples : 47 802 commentaires
Classes  : 12 catégories thématiques
Scripts  : arabe, latin, mixte, autre
Source   : YouTube
```

### Variables analysées

| Variable | Explication |
|---------|-------------|
| `text` | Le commentaire brut en Darija |
| `label` | La catégorie thématique (Sport, Religion, etc.) |
| `script` | Le système d'écriture utilisé (arabe, latin, mixte) |
| `source_type` | Type de source (commentaire YouTube, transcription) |

### Vérifications qualité effectuées

```python
pd.read_csv("Dataset_Final.csv")          # Chargement
df.isnull().sum().sum()                   # Valeurs manquantes
df['text'].duplicated().sum()             # Textes en double
df['label'].value_counts()               # Comptage par classe
```

**Ce qu'on cherche :**
- **Manquants = 0** : Aucune valeur manquante → le dataset est propre. Des valeurs manquantes pourraient planter les algorithmes ML.
- **Doublons** : Des doublons entre train et test causeraient une **data leakage** (fuite d'information) qui surévaluerait artificiellement les performances. On les supprime.
- **Déséquilibre** : Si certaines classes ont 10× plus d'exemples que d'autres, le modèle pourra être biaisé vers les classes majoritaires.

### Distribution des 12 classes — Résultats

La distribution révèle un **déséquilibre important** dans le dataset :

| Classe | ~ Nb exemples | Niveau |
|--------|---------------|--------|
| Opinion | ~8 000 | Très majoritaire |
| Soutien_Encouragement | ~6 300 | Élevé |
| Politics_Society | ~5 500 | Élevé |
| ... | ... | ... |
| Publicité_Spam | ~755 | Minoritaire |

**Ratio de déséquilibre max/min ≈ 12:1** → La classe la plus représentée a 12 fois plus d'exemples que la moins représentée.

**Conséquence critique :** Ce déséquilibre impose d'utiliser le **F1-macro** comme métrique principale (et non l'accuracy). Un modèle qui prédit toujours "Opinion" obtiendrait une bonne accuracy (car Opinion est très fréquente) mais un F1-macro très bas — le F1-macro punit ce comportement.

### Analyse de la longueur des textes

```
Moyenne  : ~85 caractères
Médiane  : ~52 caractères
```

**Observation** : La majorité des commentaires sont courts (< 100 caractères) — typique des commentaires YouTube. La médiane < moyenne indique que quelques textes très longs tirent la moyenne vers le haut.

**Impact** : Les textes courts ont moins de signal → plus difficiles à classifier. C'est pourquoi les **character n-grams** (Section 5) performent bien même sur des textes courts.

### Analyse du script (arabe vs latin)

La heatmap **scripts × classes** révèle si certaines classes sont écrites préférentiellement dans un script particulier. Cette analyse guide les choix de vectorisation : les **char n-grams** sont idéaux pour gérer la diversité des scripts.

---

## 5. Section 3 — Prétraitement Spécialisé Darija

### Pourquoi nettoyer les textes ?
Les textes bruts contiennent beaucoup de **bruit** (URLs, emojis, répétitions, diacritiques) qui ne contribuent pas à la classification. Le prétraitement **standardise** les textes pour que le modèle puisse mieux apprendre.

> **Analogie :** Avant une analyse chimique, on purifie l'échantillon. Ici, on "purifie" les textes.

### Principe fondamental : prétraitement LÉGER
Contrairement au traitement de l'anglais, on **ne supprime PAS** trop d'informations en Darija, car :
- Le **code-switching** (mélange arabe/français/amazigh) est une propriété linguistique utile qui aide à distinguer les classes
- Les **variations orthographiques** portent de l'information (ex : "bzzaf" vs "bezzaf" sont reconnaissables comme le même mot)
- Supprimer les chiffres ou le code-switching détruirait de l'information discriminante unique à la Darija

### La fonction `clean_darija()` — Explication ligne par ligne

```python
def clean_darija(text):
    text = str(text).strip()
    # 1. Supprime les URLs
    text = re.sub(r'http\S+|www\.\S+|youtu\.be/\S+', ' ', text)
    # 2. Supprime mentions et hashtags
    text = re.sub(r'[@#]\S+', ' ', text)
    # 3. Supprime les emojis
    emoji_pattern = re.compile("[\U0001F600-\U0001F64F...]", flags=re.UNICODE)
    text = emoji_pattern.sub(' ', text)
    # 4. Minuscules
    text = text.lower()
    # 5. Normalise les variantes de la lettre Alif
    text = re.sub('[إأآا]', 'ا', text)
    # 6. Normalise Ta Marbuta → Ha
    text = re.sub('ة', 'ه', text)
    # 7. Supprime les diacritiques arabes (voyelles)
    text = re.sub('[\u064B-\u065F\u0670\u0640]', '', text)
    # 8. Limite les répétitions à 2 caractères max
    text = re.sub(r'(\w)\1{2,}', r'\1\1', text)
    # 9. Supprime la ponctuation (garde arabe + mots)
    text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
    # 10. Normalise les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else "vide"
```

### Tableau de transformation

| Opération | Exemple avant | Exemple après | Raison |
|-----------|---------------|---------------|--------|
| Supprimer URLs | `http://youtube.com/...` | `(supprimé)` | Pas de valeur discriminante |
| Supprimer mentions | `@user123` | `(supprimé)` | Noms d'utilisateurs sans sens thématique |
| Supprimer emojis | `😂🔥` | `(supprimé)` | Encodage unicode complexe, peu fiable |
| Minuscules | `Allah` | `allah` | Normalisation pour éviter duplicats |
| Normaliser Alif | `إ أ آ` | `ا` | Même lettre, 4 formes différentes en arabe |
| Normaliser Ta Marbuta | `ة` | `ه` | Même son, deux écritures |
| Supprimer diacritiques | `كَتَبَ` | `كتب` | Les voyelles arabes sont optionnelles à l'écrit |
| Limiter répétitions | `waaaw` → | `waaw` | "haaaaaa" ≡ "haa" pour le sens |
| Supprimer ponctuation | `!?.,;:` | `(espaces)` | Pas de sens thématique |

### Résultats de performance
Le prétraitement tourne à **plusieurs milliers de textes par seconde**, ce qui est suffisant pour notre corpus de 47 802 textes.

### Vérification de la qualité
Après prétraitement, on vérifie sur 3 exemples que :
- Les URLs, mentions, emojis ont bien disparu
- Les lettres arabes sont normalisées (une seule forme pour la même lettre)
- Les répétitions sont limitées à 2
- Le texte latin reste intact (code-switching préservé)

---

## 6. Section 4 — Séparation Train / Test

### Pourquoi séparer les données ?
Le modèle doit être évalué sur des données **qu'il n'a JAMAIS vues** pendant l'entraînement. Sinon, c'est comme donner à un étudiant les réponses de l'examen avant — les notes ne mesurent rien.

> **Règle d'or du ML :** Le test set est "sacré" — on ne le touche qu'à la toute fin.

### La division 80/20

```
Dataset complet : 47 802 exemples
    ↓
Train set : 38 241 exemples (80%) → pour apprendre
Test set  :  9 561 exemples (20%) → pour évaluer
```

**Pourquoi 80/20 ?** C'est la règle empirique standard :
- **80% train** → assez de données pour que le modèle apprenne correctement
- **20% test** → assez de données pour une évaluation statistiquement fiable (~9 500 exemples = base solide)

### Le `LabelEncoder` — Conversion des labels

```python
le = LabelEncoder()
df['label_enc'] = le.fit_transform(df['label'])
```

Les algorithmes ML travaillent avec des **nombres**, pas des mots. LabelEncoder convertit :
- "Sport" → 0
- "Religion" → 1
- "Food_Cuisine" → 2
- ... etc.

`le.classes_` mémorise la correspondance pour pouvoir reconvertir dans l'autre sens.

### Le paramètre `stratify=y` — Crucial pour les données déséquilibrées

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=SEED, stratify=y)
```

**Sans `stratify`** : par hasard, certaines classes minoritaires pourraient se retrouver presque entièrement dans le train set, rendant leur évaluation impossible.

**Avec `stratify=y`** : la proportion de chaque classe est **identique** dans train et test. Si "Publicité_Spam" représente 1.5% du corpus complet, elle représentera aussi ~1.5% du train et ~1.5% du test.

### Vérification de la stratification

```
Écart max de distribution train/test : < 0.01% → OK
```

L'écart inférieur à 1% confirme que le split stratifié a bien fonctionné.

---

## 7. Section 5 — Vectorisation (Transformer les Textes en Nombres)

### Pourquoi vectoriser ?
Les algorithmes de ML ne comprennent que les **nombres**, pas les mots. La vectorisation transforme chaque texte en un **vecteur de nombres** (un tableau de valeurs numériques) que l'algorithme peut calculer.

> **Analogie :** C'est comme encoder les mots en coordonnées GPS — on transforme quelque chose d'abstrait (un texte) en quelque chose de calculable (un point dans l'espace mathématique).

### Les 5 représentations testées

#### 1. BoW — Bag of Words (Sac de Mots)
```
Texte : "l match kan mezyan"
Vocabulaire : {match: 5, kan: 2, mezyan: 8, ...}
Vecteur BoW : [0, 0, 1, 0, 1, 1, 0, ...]
                           ↑match ↑kan ↑mezyan
```
**Principe** : Compte le nombre de fois que chaque mot apparaît.
**Problème** : "le" et "la" apparaissent souvent mais ne distinguent pas les classes → même poids qu'un mot rare et informatif.

#### 2. TF-IDF Word (1,2-grams)
```
TF  = fréquence du mot dans CE texte
IDF = log(N / nb_textes_avec_ce_mot) = rareté du mot

TF-IDF = TF × IDF
```
**Plus le poids est élevé** = mot fréquent dans ce texte ET rare dans le corpus = mot **discriminant**.
- `sublinear_tf=True` → applique log(TF+1) pour atténuer les mots très fréquents
- `ngram_range=(1,2)` → capture aussi les **bigrammes** ("match mezyan", "bzzaf lkul")

#### 3. TF-IDF Caractères (2,4-grams)
Au lieu des mots, on découpe le texte en séquences de **2 à 4 caractères** :
```
"mezyan" → "me", "ez", "zy", "ya", "an", "mez", "ezy", "zya", "yan", "mezy", "ezya", "zyan"
```
**Pourquoi c'est idéal pour la Darija ?**
- Robuste aux **fautes d'orthographe** : "mezyan" et "mzyan" partagent "ezy", "zya", "yan"
- Robuste au **code-switching** : caractères arabes et latins coexistent
- Fonctionne bien sur les **textes courts** (génère plus de features par mot)

#### 4. TF-IDF Combiné (word + char)
```python
Xtr_combined = hstack([Xtr_word, Xtr_char], format='csr')
```
Concaténation horizontale des deux matrices : on obtient une représentation plus riche combinant la précision des mots (sens global) et la robustesse des caractères (variations orthographiques). C'est la représentation la plus puissante pour la Darija.

#### 5. TF-IDF mixte char+word (ngram 1,3)
Variante intermédiaire testée dans le benchmark.

### Résultats de la vectorisation

| Représentation | Features | Densité | Temps | Interprétation |
|---|---|---|---|---|
| BoW (word unigrams) | 80 000 | 0.021% | 3.4s | Vocabulaire tronqué à 80k mots |
| TF-IDF (word 1-2grams) | 81 013 | 0.021% | 3.7s | Bigrammes ajoutent des features |
| **TF-IDF (char 2-4grams)** | **77 504** | **0.213%** | **7.7s** | **10× plus dense → meilleure performance** |
| TF-IDF (char+word mixte) | 24 467 | 0.550% | 6.0s | Peu de features mais très denses |
| TF-IDF combined | **130 000** | — | 21.3s | **Fusion : représentation la plus riche** |

### Concept crucial : la densité

La **densité** mesure la proportion de valeurs non-nulles dans la matrice.

**BoW : densité = 0.021%** → sur 80 000 colonnes, un commentaire de 10 mots n'en "active" que ~17. C'est une **matrice creuse (sparse)**.

**TF-IDF char 2-4grams : densité = 0.213%** → 10× plus dense. Un mot de 6 lettres génère environ 11 n-grams de caractères, ce qui rend la représentation plus riche.

**Représentation combined : 130 000 features** = word (50k) + char (80k). La plus riche mais la plus lente.

**Pourquoi les matrices creuses sont importantes ?** `scipy.sparse` stocke efficacement ces matrices en ne gardant que les valeurs non-nulles → gain de mémoire énorme (facteur 1000+). Sans ce format, une matrice 38241 × 130000 prendrait ~20 GB de RAM !

### Important : le vectoriseur est **ajusté sur le train set uniquement**

```python
vec.fit_transform(X_train)  # Apprend le vocabulaire depuis le train
vec.transform(X_test)       # Applique le même vocabulaire au test
```

On ne doit **jamais** utiliser `fit_transform` sur le test set — sinon on utilise des informations du test pendant l'entraînement (data leakage).

---

## 8. Section 6 — Définition des Modèles de Classification

### Qu'est-ce qu'un classifieur ?
Un classifieur est un algorithme qui, à partir d'un vecteur de nombres (le texte transformé), **prédit la classe** (la catégorie) du texte.

> **Analogie :** C'est comme un expert qui, après avoir examiné les "empreintes" d'un texte (ses vecteurs TF-IDF), dit "ce texte parle de sport" ou "ce texte est politique".

### Les 7 modèles testés — Description détaillée

#### 1. Logistic Regression (LR)
**Principe** : Trouve une frontière linéaire dans l'espace vectoriel qui sépare les classes. Calcule la probabilité d'appartenance à chaque classe via la fonction sigmoïde/softmax.
```
Score(classe k) = w₁x₁ + w₂x₂ + ... + wₙxₙ + b
```
Chaque feature (n-gram) a un poids `wᵢ` appris pendant l'entraînement.

**Forces pour NLP** : Excellente avec TF-IDF, rapide, **interprétable** (on peut voir quels tokens ont les poids les plus élevés pour chaque classe).

**Paramètre C=5.0** : Régularisation. Un C élevé signifie moins de régularisation → le modèle peut s'adapter plus finement aux données.

#### 2. Complement Naive Bayes (CNB)
**Principe** : Variante de Naive Bayes qui modélise le **complémentaire** de chaque classe (au lieu de modéliser directement la classe). 
Formule de base (Naive Bayes) : `P(classe|texte) ∝ P(classe) × ∏P(mot|classe)`
"Naive" car il suppose l'indépendance entre les mots (approximation forte).

**Forces** : Spécifiquement conçu pour les datasets **déséquilibrés**, très rapide.
**Paramètre `alpha=0.1`** : Lissage de Laplace — évite les probabilités nulles pour les mots jamais vus.

#### 3. Linear SVC (Support Vector Classifier)
**Principe** : Cherche l'**hyperplan de marge maximale** qui sépare les classes dans l'espace vectoriel.
```
Maximiser la marge entre les classes → meilleure généralisation
```
C'est le **modèle de référence en NLP** pour la classification de texte.

**CalibratedClassifierCV** : LinearSVC de base ne donne que des classes, pas des probabilités. Cette enveloppe (cv=3) apprend à calibrer des probabilités en 3-fold cross-validation.

#### 4. SGD Classifier
**Principe** : Descente de gradient stochastique — met à jour les poids du modèle **exemple par exemple** (ou mini-batch).
```
Pour chaque exemple : w = w - α × ∇L(w, xᵢ, yᵢ)
```
**`loss='modified_huber'`** : Fonction de perte robuste, équivalente à une SVM mais avec calibration de probabilités intégrée.
**Forces** : Scalable pour très grands datasets, entraînement rapide.

#### 5. Random Forest (RF)
**Principe** : **Ensemble** de 200 arbres de décision entraînés sur des sous-ensembles aléatoires des données et des features. La prédiction finale est le vote à la majorité.
```
200 arbres de décision → vote → classe gagnante
```
**`min_samples_leaf=2`** : Chaque feuille doit avoir au moins 2 exemples → contrôle l'overfitting.

#### 6. Extra Trees
Comme Random Forest mais avec des **seuils de coupure aléatoires** pour chaque feature (au lieu du meilleur seuil trouvé). Plus rapide que RF avec une performance similaire, et parfois meilleur en généralisation.

#### 7. Ridge Classifier
Régression Ridge (L2) adaptée à la classification. Résout un problème d'optimisation quadratique directement — très rapide à entraîner mais moins flexible que LR ou SVC.

### Paramètres communs importants

| Paramètre | Signification | Impact |
|-----------|---------------|--------|
| `class_weight='balanced'` | Donne automatiquement plus de poids aux classes rares | Compense le déséquilibre 12:1 |
| `random_state=SEED` | Reproductibilité | Même résultat à chaque exécution |
| `n_jobs=-1` | Utilise tous les cœurs CPU | Entraînement parallèle plus rapide |
| `max_iter=1000` | Nombre max d'itérations d'optimisation | Garantit la convergence |

### Total de combinaisons
**5 vectoriseurs × 7 modèles = 35 combinaisons** → toutes testées dans la section suivante.

---

## 9. Section 7 — Benchmark Systématique : 35 Combinaisons

### Qu'est-ce qu'un benchmark ?
Un benchmark est une **comparaison systématique** de toutes les solutions sur les mêmes données et les mêmes métriques — comme une course où tous les coureurs font exactement le même parcours dans les mêmes conditions.

### Protocole d'évaluation

Pour chaque paire (vectoriseur, modèle) :
1. **Entraîner** le modèle sur `X_train` → apprentissage des paramètres
2. **Prédire** sur `X_test` (données jamais vues) → évaluation réelle
3. **Calculer** : Accuracy, Precision, Recall, F1-macro, F1-weighted
4. **Calculer l'overfit gap** = F1_train - F1_test

### Les 5 métriques expliquées

**Exemple concret pour la classe "Sport" :**

| Métrique | Formule | Définition | Interprétation |
|----------|---------|-----------|----------------|
| **Accuracy** | (TP+TN) / Total | % de textes bien classés | Trompeuse si classes déséquilibrées |
| **Precision** | TP / (TP+FP) | Sur 100 prédits "Sport", combien sont vrais Sport ? | Qualité des prédictions |
| **Recall** | TP / (TP+FN) | Sur 100 vrais Sport, combien trouvés ? | Complétude |
| **F1-macro** | Moyenne harmonique P×R, par classe, puis moyenne simple | Traite équitablement les 12 classes | **Métrique principale** |
| **F1-weighted** | Comme F1-macro mais pondéré par le support | Favorable aux classes majoritaires | Secondaire |

**Overfit gap** = F1_train - F1_test : si élevé → le modèle mémorise au lieu de généraliser.

### Pourquoi F1-macro et pas Accuracy ?
Avec un ratio de déséquilibre de 12:1, un modèle qui **prédit toujours "Opinion"** (la classe la plus fréquente) obtiendrait une bonne accuracy (~16-17%) mais un **F1-macro très bas** (~0.01) car il ne prédit jamais les 11 autres classes. Le F1-macro "punit" ce comportement.

### Résultats du Benchmark — Top 5

| Rang | Modèle | Vectoriseur | F1-macro | Accuracy | Overfit |
|------|--------|-------------|----------|----------|---------|
| 🥇 1 | **Linear SVC** | TF-IDF char 2-4grams | **0.604** | **0.634** | +0.336 |
| 2 | SGD Classifier | TF-IDF combined word+char | 0.600 | — | +0.345 |
| 3 | Linear SVC | TF-IDF combined word+char | 0.600 | — | +0.386 |
| 4 | Logistic Regression | TF-IDF combined word+char | 0.597 | — | +0.390 |
| 5 | Logistic Regression | TF-IDF char 2-4grams | 0.596 | — | +0.327 |

### Observations générales du benchmark

**Les scores F1-macro varient entre 0.38 et 0.60** → performances globalement modestes, ce qui est attendu pour une langue peu dotée comme la Darija avec 12 classes très diverses.

**Le vectoriseur TF-IDF char 2-4grams domine systématiquement** toutes les autres représentations. Cela confirme que les n-grams de caractères sont la meilleure approche pour gérer l'orthographe non-standardisée de la Darija.

**Le BoW est systématiquement le moins performant** — il traite les variations orthographiques comme des mots entièrement différents, sans aucun lien entre "mezyan" et "mzyan".

**Le surapprentissage (overfit) est le problème dominant** : il oscille entre +0.10 et +0.48, ce qui signifie que les modèles mémorisent le train set sans bien généraliser. Ce n'est pas une anomalie — c'est une propriété connue des modèles TF-IDF sur des langues peu dotées.

### Interprétation des heatmaps

**Heatmap F1-macro** : Visualise les performances de toutes les combinaisons. La colonne TF-IDF char 2-4grams est systématiquement la plus sombre (meilleure), la colonne BoW la plus claire (moins performante).

**Heatmap Overfit Gap** : La colonne TF-IDF combined montre un overfit plus élevé que char seul, malgré des scores F1 similaires — confirmation que la combinaison n'apporte pas assez de valeur ajoutée pour justifier son coût en overfitting.

### Conclusion du benchmark

> **Champion : Linear SVC + TF-IDF char 2-4grams**
> F1-macro = 0.604 | Accuracy = 0.634 | Overfit = +0.336
> Ce modèle est le meilleur compromis global.

---

## 10. Section 8 — Analyse Approfondie du Meilleur Modèle

### Pourquoi analyser en détail ?
Un seul chiffre F1-macro ne suffit pas. On veut savoir :
- Le modèle est-il bon sur **toutes** les classes ou seulement sur les majoritaires ?
- Quelles classes **confond-il** souvent entre elles ?
- Y a-t-il des **patterns systématiques** dans les erreurs ?

### Rapport de classification — Métriques par classe

Pour chaque classe, on obtient :

| Classe | Precision | Recall | F1-score | Support | Niveau |
|--------|-----------|--------|----------|---------|--------|
| **Food_Cuisine** | ~0.795 | ~0.794 | **0.794** | ~800 | Excellent |
| **Soutien_Encouragement** | — | — | **0.752** | ~1678 | Très bon |
| **Religion** | — | — | **0.725** | — | Très bon |
| Health_Science | — | — | 0.697 | — | Bon |
| Business_Economy | — | — | 0.662 | — | Correct |
| Politics_Society | — | — | 0.657 | — | Correct |
| Sports_Fitness | — | — | ~0.698 | — | Bon |
| Publicité_Spam | — | 0.513 | 0.582 | ~152 | Faible (volume) |
| Opinion | 0.446 | 0.560 | **0.496** | ~1785 | Problématique |
| Question | — | 0.454 | 0.491 | — | Problématique |
| Inclassable_Bruit | — | — | 0.418 | — | Problématique |
| **Entertainment** | — | 0.216 | **0.278** | ~342 | Pire classe |

### Analyse par groupe de performance

#### Classes bien maîtrisées (F1 ≥ 0.70)

**Food_Cuisine (0.794)** : Vocabulaire spécifique et peu ambigu — noms de plats marocains, ingrédients, recettes. Le modèle identifie facilement ces textes car les n-grams de caractères capturent des motifs très distinctifs (les noms de plats marocains ont des patterns orthographiques reconnaissables).

**Religion (0.725)** : Le vocabulaire religieux islamique en arabe/Darija est extrêmement spécifique et consistant. Les termes comme "llah", "nbi" (prophète), "sala" (prier), "hram" (interdit) créent des n-grams de caractères très discriminants.

**Soutien_Encouragement (0.752)** : Expressions récurrentes et ton émotionnel distinctif. La classe est aussi très représentée (~6300 exemples) — le volume aide.

#### La classe "Opinion" — Le paradoxe volume vs qualité

**F1 = 0.496 malgré 1785 exemples** — c'est le résultat le plus révélateur du projet.

**Pourquoi ?** La classe Opinion regroupe probablement des commentaires du type :
- "hada machi mzyan" → critique politique (→ devrait être Politics)
- "3ajbni had lfilm" → avis sur un film (→ devrait être Entertainment)
- "lmatch kan zwine" → opinion sur un match (→ devrait être Sports)
- "rabbi y3awnak" → encouragement (→ devrait être Soutien)

Le modèle reçoit des textes **très variés** sous la même étiquette "Opinion". Il ne peut pas apprendre une frontière claire parce qu'il n'en existe pas — c'est un problème d'annotation, pas un problème algorithmique.

**Preuve dans les chiffres :**

| Métrique | Opinion | Food_Cuisine |
|----------|---------|--------------|
| Précision | 0.446 | 0.795 |
| Recall | 0.560 | 0.794 |
| F1 | 0.496 | 0.794 |
| Support | 1 785 | 800 |

Food_Cuisine avec **moins d'exemples** fait bien mieux car ses textes se ressemblent. Opinion avec **plus d'exemples** fait mal car ses textes ne se ressemblent pas entre eux.

#### Entertainment — La pire classe (F1 = 0.278)

Seulement 1 texte sur 5 correctement identifié. Le recall est désastreux (0.216). Le problème : le contenu Entertainment en Darija (réactions, célébrités, musique) ressemble fortement à des opinions subjectives. Le modèle ne voit pas la différence avec TF-IDF seul — seuls des embeddings contextuels (BERT) peuvent y voir quelque chose.

### La Matrice de Confusion — Explication

```
                Prédit Sport  Prédit Opinion  Prédit Religion
Vrai Sport          85              18              2        → Recall Sport = 85/105 = 81%
Vrai Opinion        12             560             15        → Recall Opinion = 560/1000 = 56%
Vrai Religion        1               5             90        → Recall Religion = 90/96 = 94%
         ↑
    Precision Sport = 85/(85+12+1) ≈ 87%
```

**Diagonale** = bonnes prédictions (à maximiser)
**Hors diagonale** = erreurs → les cases chaudes révèlent les confusions fréquentes

**Opinion comme attracteur universel :** La matrice révèle qu'Opinion capte les erreurs de presque toutes les autres classes. Quand le modèle est incertain, il prédit "Opinion" par défaut, car cette classe est très présente dans les données d'entraînement.

**Exemple des fuites vers Opinion :**
- Business_Economy → Opinion : 9% des exemples Business
- Politics_Society → Opinion : 17% des exemples Politics
- Inclassable_Bruit → Opinion : 30% des exemples Bruit
- Question → Opinion : 20% des exemples Question

---

## 11. Section 9 — Méthodes d'Ensemble

### Principe
Au lieu d'utiliser un seul modèle, on en **combine plusieurs** pour obtenir un meilleur résultat.

> **Analogie :** Plutôt que de demander l'avis d'un seul expert, on consulte 4 experts et on prend la décision qui a la majorité.

### Les 3 stratégies testées

#### Hard Voting
```
Modèle 1 prédit : Sport
Modèle 2 prédit : Sport
Modèle 3 prédit : Politique
Modèle 4 prédit : Sport
→ Résultat final : Sport (3 votes sur 4)
```
**Résultat : F1 = 0.6039** — légèrement en dessous du meilleur modèle seul. Les 4 modèles de base sont trop similaires (tous linéaires) et font les mêmes erreurs ensemble.

#### Soft Voting
```
Modèle 1 : P(Sport)=0.80, P(Politique)=0.20
Modèle 2 : P(Sport)=0.75, P(Politique)=0.25
Modèle 3 : P(Sport)=0.40, P(Politique)=0.60
Modèle 4 : P(Sport)=0.85, P(Politique)=0.15
→ Moyenne : P(Sport)=0.70 → Sport
```
Plus précis car tient compte de la **confiance** de chaque modèle. **Résultat : F1 = 0.6123** (+0.008 vs meilleur seul).

#### Stacking (Empilage)
```
Niveau 1 : Modèles de base (LR, SVC, NB, Ridge)
           → Produisent des prédictions
           
Niveau 2 : Meta-classifieur (LR) entraîné sur les prédictions du niveau 1
           → Apprend QUELS modèles croire selon le contexte
```
**`passthrough=True`** : Les features originales sont aussi transmises au méta-classifieur.
**`cv=5`** : Validation croisée interne pour éviter la data leakage dans l'entraînement du méta-modèle.

**Résultat : F1 = 0.6207** (+0.016 vs meilleur seul). Meilleur résultat global mais au prix de **895 secondes** de calcul.

### Tableau comparatif des ensembles

| Méthode | F1-macro | Temps | Gain | Verdict |
|---------|----------|-------|------|---------|
| Linear SVC seul (référence) | 0.6043 | ~Xs | — | Référence |
| Hard Voting | 0.6039 | 113s | -0.0004 | À rejeter |
| Soft Voting | 0.6123 | 197s | +0.0080 | Acceptable |
| **Stacking** | **0.6207** | **895s** | **+0.0164** | Meilleur résultat |

### Pourquoi les gains sont-ils si modestes ?
Les 4 modèles de base partagent la même famille (classifieurs linéaires) et le même vectoriseur (TF-IDF char 2-4grams) → **les mêmes erreurs systématiques**. Un ensemble est efficace quand ses membres sont **diversifiés** et font des erreurs **différentes**.

---

## 12. Section 10 — Optimisation des Hyperparamètres

### Qu'est-ce qu'un hyperparamètre ?
Un hyperparamètre est un réglage qu'on choisit **avant** l'entraînement (par opposition aux paramètres que le modèle apprend pendant).

> **Analogie :** Pour un four, la température et le temps de cuisson sont des hyperparamètres — on les fixe avant de commencer. La recette optimale n'est pas connue d'avance, on doit la trouver.

### HalvingGridSearchCV — L'algorithme Successive Halving

Au lieu de tester toutes les combinaisons sur toutes les données (GridSearchCV classique, très coûteux), l'algorithme **élimine progressivement** les mauvais candidats :

```
Itération 0 : 12 candidats  sur  4 780 exemples  → 60 fits
Itération 1 :  6 candidats  sur  9 560 exemples  → 30 fits  (50% éliminés)
Itération 2 :  3 candidats  sur 19 120 exemples  → 15 fits  (50% éliminés)
Itération 3 :  2 candidats  sur 38 240 exemples  → 10 fits  (données complètes)
```

**Résultat** : 3 à 5× plus rapide que GridSearchCV classique pour des résultats similaires.

### Espace de recherche testé

| Hyperparamètre | Valeurs testées | Rôle |
|---------------|-----------------|------|
| `C` | [0.5, 1.0, 2.0, 5.0, 10.0, 20.0] | Régularisation (compromis biais-variance) |
| `solver` | ['lbfgs', 'saga'] | Algorithme d'optimisation |

### Résultats du GridSearch

**Meilleurs paramètres trouvés :** `C=10.0, solver=lbfgs`

| Métrique | Logistic Regression optimisée | Linear SVC de base | Écart |
|----------|-------------------------------|---------------------|-------|
| F1 CV (validation croisée) | 0.5845 | — | — |
| **F1 test** | **0.5949** | **0.6043** | **-0.0094** |
| Temps de calcul | 1 726 secondes (~29 min) | quelques secondes | ×100 |

### Analyse : pourquoi le GridSearch n'améliore pas ?

**29 minutes de calcul pour un résultat inférieur au modèle de base.** Plusieurs raisons :

**1. La LR est structurellement moins adaptée que SVC** : Le Linear SVC optimise directement la marge de séparation (hinge loss), plus robuste sur des espaces de très haute dimension (97 389 features). La LR optimise une probabilité (log loss) — moins efficace dans ce contexte.

**2. Le vrai plafond est atteint** : Avec des features TF-IDF classiques, les modèles linéaires convergent tous vers F1 ≈ 0.59-0.62. Le GridSearch ne peut pas dépasser cette limite — elle est imposée par la **représentation des données**, pas par les hyperparamètres.

**Leçon essentielle :** Optimiser un mauvais modèle ne le rend pas bon. La solution ne viendra pas d'un meilleur C ou solver, mais d'un **changement de représentation** : embeddings contextuels capables de capturer la sémantique que les n-grams de surface ne voient pas.

---

## 13. Section 11 — Courbes d'Apprentissage

### Qu'est-ce qu'une courbe d'apprentissage ?
Elle montre comment la **performance évolue** quand on donne plus de données au modèle.

> **Analogie :** C'est comme mesurer comment un étudiant progresse selon le nombre d'heures de révision. Après un certain point, plus d'heures n'améliorent plus les notes (plateau).

### Interprétation visuelle

```
F1
1.0 |_____________________ ← Train score (quasi-parfait)
    |
0.80|
    |    /
0.60|___/_________________ ← Val score (monte lentement)
    |
0.40|
    +--+--+--+--+--+--→ Nb exemples d'entraînement
      10% 20% 40% 60% 80% 100%
```

**Courbe bleue (entraînement) ≈ 0.99** : Le modèle mémorise parfaitement les données d'entraînement.
**Courbe rouge (validation) monte lentement** : La validation progresse avec les données, mais beaucoup moins vite.

### Les données chiffrées

| Volume | Exemples | F1 Train | F1 Validation | Gap |
|--------|----------|----------|---------------|-----|
| 10% | 3 055 | 0.9988 | 0.4588 | **0.540** |
| 20% | 6 115 | 0.9977 | 0.4903 | 0.507 |
| 40% | 12 233 | 0.9924 | 0.5476 | 0.445 |
| 60% | 18 351 | 0.9889 | 0.5687 | 0.420 |
| 80% | 24 469 | 0.9842 | 0.5721 | 0.412 |
| **100%** | 30 592 | 0.9787 | 0.5836 | **0.395** |

### Diagnostic : surapprentissage sévère

**Overfit gap final : +0.395** → Le modèle vit dans deux mondes parallèles : excellent sur ce qu'il a vu (F1=0.98), moyen sur ce qu'il n'a pas vu (F1=0.58).

**Pourquoi C=10 aggrave l'overfit ?**
- C élevé = régularisation faible = le modèle s'adapte très finement aux données d'entraînement → mémorisation
- C faible = régularisation forte = le modèle est forcé de trouver des règles plus générales

**Les deux courbes vont-elles se rejoindre ?** Non. À ce rythme de réduction du gap (0.145 pour ×10 données), il faudrait **multiplier le dataset par 5 à 10** (150 000 à 300 000 exemples) pour espérer rapprocher significativement les deux courbes.

**Les leviers disponibles :**

| Levier | Impact attendu | Difficulté |
|--------|---------------|------------|
| Réduire C (ex: 0.1, 0.01) | Réduire l'overfit gap | Facile |
| Augmenter le dataset | Monter la courbe rouge | Moyen |
| Réviser les annotations | Réduire le bruit | Difficile |
| Changer de représentation (embeddings) | Briser le plafond | Difficile |

---

## 14. Section 12 — WordClouds par Classe

### Qu'est-ce qu'un WordCloud ?
Un nuage de mots affiche les mots les plus fréquents — les mots les plus grands sont les plus fréquents. C'est une **visualisation qualitative** du vocabulaire caractéristique de chaque classe.

**Utilité** : Permet de valider intuitivement que notre modèle "voit" les bons mots et que chaque classe a un vocabulaire propre reconnaissable.

### Défi technique : l'arabe en WordCloud

L'arabe s'écrit de **droite à gauche (RTL)** et les lettres se lient différemment selon leur position dans le mot. Un rendu naïf donnerait des lettres déconnectées et illisibles.

**Solution en 2 étapes :**
1. **`arabic_reshaper`** → relie les lettres arabes correctement (une lettre arabe peut avoir 4 formes selon sa position : isolée, début, milieu, fin de mot)
2. **`python-bidi`** (Bidirectional algorithm) → inverse l'ordre des caractères pour l'affichage RTL

**Exemple :**
```
Avant reshaping : م ز ي ا ن (lettres séparées, illisibles dans un rendu classique)
Après reshaping : مزيان (mot complet, lisible)
```

### Ce que les WordClouds révèlent

Les WordClouds confirment visuellement les diagnostics du modèle :
- **Food_Cuisine** : vocabulaire culinaire dense et spécifique (tajine, couscous, lhut...)
- **Religion** : termes religieux très fréquents (allah, nbi, sala, baraka...)
- **Opinion** : vocabulary dispersé, emprunte à toutes les autres classes → confirme pourquoi c'est une classe difficile

---

## 15. Section 13 — Visualisation t-SNE

### Problème : comment visualiser 100 000 dimensions ?
Nos vecteurs TF-IDF ont 100 000+ dimensions. L'œil humain ne peut voir que 2D ou 3D. **t-SNE** résout ce problème : il projette les données de haute dimension en 2D en préservant les **relations de proximité**.

> **Analogie :** C'est comme prendre une carte 3D d'une ville et l'"aplatir" en 2D en préservant les quartiers — les lieux proches restent proches.

### L'algorithme en 2 étapes

**Étape 1 : TruncatedSVD** (SVD tronquée = décomposition en valeurs singulières)
```
100 000 dimensions → 50 dimensions
```
Préserve la variance maximale. Beaucoup plus rapide que directement 100000D → 2D.

**Étape 2 : t-SNE** (t-distributed Stochastic Neighbor Embedding)
```
50 dimensions → 2 dimensions
```
Minimise la divergence KL entre les distributions de distances en haute et basse dimension.
- `perplexity=40` : compromis structure locale/globale (recommandé : 5-50)
- `max_iter=1000` : nombre d'itérations d'optimisation
- Travaille sur un échantillon stratifié de **3000 exemples** (t-SNE est O(n²) → lent sur grands datasets)

### Résultats et interprétation

**Observation principale : pas de clusters nets** → les classes Darija sont massivement entremêlées dans l'espace TF-IDF.

**Classes avec tendance au regroupement :** Food_Cuisine (îlots visibles), Religion (petits regroupements), Soutien_Encouragement (zones de densité).

**Classes totalement noyées dans le nuage :** Opinion (dispersée sur toute la visualisation), Entertainment (fondue dans le nuage central), Inclassable_Bruit (éparpillée aléatoirement).

**Ce que le t-SNE prouve :**
- Les features TF-IDF ne séparent pas bien les classes Darija
- Les classes thématiques fortes émergent légèrement, mais la majorité des textes reste indistinguable par des features de surface
- C'est l'argument visuel le plus fort en faveur d'un changement vers des embeddings contextuels

---

## 16. Section 14 — Calibration et Confiance du Modèle

### Qu'est-ce que la calibration ?
Un modèle **bien calibré** est un modèle dont les probabilités prédites correspondent à la réalité.

**Exemple :** Si le modèle dit "je suis sûr à 80% que c'est du Sport" sur 100 textes, alors 80 de ces textes doivent effectivement être du Sport.

### Résultats — Distribution de la confiance

```
Moyenne  = 0.674
Médiane  = 0.680
```

La distribution est **bimodale** :
- Groupe 1 (~0.2–0.5) : prédictions hésitantes (classes floues comme Opinion, Entertainment)
- Groupe 2 (~0.95–1.0) : prédictions très confiantes (classes nettes comme Food, Religion)

### Analyse de la courbe Accuracy vs Seuil de confiance

| Seuil de confiance | % prédictions conservées | Accuracy |
|-------------------|--------------------------|----------|
| ≥ 0.50 | 72.6% | 0.711 |
| ≥ 0.60 | 59.7% | 0.756 |
| ≥ 0.70 | 47.9% | 0.803 |
| ≥ 0.80 | 36.4% | 0.846 |
| ≥ 0.90 | 24.1% | 0.895 |
| **≥ 0.95** | **15.7%** | **0.929** |

**Ce que cela signifie concrètement :** Le modèle peut atteindre **92.9% d'accuracy** en ne répondant que sur les **15.7% de cas où il est très sûr**. En production, cela ouvre une stratégie puissante :

```
Confiance ≥ 0.90  →  Prédiction automatique (accuracy ~89%)
Confiance < 0.90  →  Renvoyer vers révision humaine ou "Indéterminé"
```

### Confiance moyenne par classe

La confiance du modèle reproduit fidèlement le classement par F1-score :

| Niveau | Classes | Confiance | F1 |
|--------|---------|-----------|-----|
| Très haute | Soutien, Food | ~0.76-0.78 | >0.75 |
| Haute | Religion, Politics | ~0.70-0.74 | >0.65 |
| Faible | Opinion, Spam | ~0.61-0.63 | ~0.55 |
| Très faible | Entertainment, Question | ~0.52-0.56 | <0.50 |

**Le modèle sait quand il se trompe.** Sa confiance est un indicateur fiable de sa propre performance — propriété précieuse pour un système de production.

### Recommandation pour la mise en production

```python
if confiance >= 0.80:
    → Prédiction automatique        # 36% des cas, accuracy ~85%
elif confiance >= 0.60:
    → Prédiction avec avertissement # 24% des cas, accuracy ~75%
else:
    → "Indéterminé" / révision      # 40% des cas, trop incertain
```

---

## 17. Section 15 — Features les Plus Discriminantes

### Principe de l'interprétabilité

Dans la Régression Logistique, chaque token (mot ou n-gram de caractères) a un **poids** appris pendant l'entraînement :
- **Poids positif élevé** → ce token pousse fortement vers cette classe
- **Poids négatif élevé** → ce token pousse fortement contre cette classe

C'est l'un des grands avantages de la LR : on peut **expliquer** pourquoi le modèle prédit une classe. Les méthodes comme Random Forest ou BERT sont des "boîtes noires" — on ne peut pas facilement expliquer leurs décisions.

### Résultats par classe

**Food_Cuisine** : Les barres bleues sont les plus longues et les plus nombreuses parmi toutes les classes. Le vocabulaire culinaire marocain est riche et unique → n-grams de caractères très spécifiques (noms de plats, ingrédients).

**Religion** : **Signal le plus fort de toutes les classes** — la barre bleue dominante est la plus longue du graphique. Le vocabulaire religieux islamique en arabe/Darija est extrêmement spécifique (llah, nbi, sala, hram, janna...).

**Opinion** : Le graphique le plus révélateur — les barres bleues et rouges sont nombreuses mais de petite taille. Aucune feature ne domine. Le modèle a appris beaucoup de petits signaux contradictoires → Opinion n'a pas de vocabulaire propre.

**Entertainment** : Des barres bleues de longueur modérée — signal moins fort que Food ou Religion. Le modèle reconnaît Entertainment **par exclusion** plus que par signal positif fort, ce qui explique son mauvais recall.

### Synthèse — Qualité du signal par classe

| Classe | Signal | Netteté | Diagnostic |
|--------|--------|---------|------------|
| Religion | ⬛⬛⬛⬛⬛ | Très net | Vocabulaire arabe unique |
| Food_Cuisine | ⬛⬛⬛⬛⬛ | Très net | Termes culinaires spécifiques |
| Publicité_Spam | ⬛⬛⬛⬛ | Net | Langage promotionnel distinct |
| Soutien | ⬛⬛⬛⬛ | Net | Expressions récurrentes |
| Sports | ⬛⬛⬛ | Correct | Léger overlap Soutien |
| Question | ⬛⬛ | Faible | Marqueurs peu exclusifs |
| Entertainment | ⬛⬛ | Faible | Classe hétérogène |
| **Opinion** | **⬛** | **Très faible** | **Aucun vocabulaire propre** |

---

## 18. Section 16 — Tableau de Bord Final (Dashboard)

### Composition du dashboard

Un dashboard rassemble les informations les plus importantes en un seul coup d'œil — comme le tableau de bord d'une voiture.

**Les 6 panels :**
1. **Distribution des classes** → Déséquilibre visible (Opinion >> Entertainment)
2. **Heatmap F1-macro** → Vue d'ensemble du benchmark (colonnes char les plus sombres)
3. **F1 par classe** → Performances individuelles du champion (Food/Religion verts, Entertainment rouge)
4. **Individuels vs Ensembles** → Stacking est le meilleur (+1.6 points)
5. **Distribution de confiance** → Distribution bimodale (très sûr ou très incertain)
6. **Tableau de métriques** → Bilan chiffré final

### Métriques finales du dashboard

| Indicateur | Valeur |
|------------|--------|
| F1-macro | 0.5949 (GridSearch) / 0.6207 (Stacking) |
| Accuracy | 0.6195 (GridSearch) / 0.6409 (Stacking) |
| Nb classes | 12 |
| Combinaisons testées | 35 |
| Train size | 38 241 |
| Test size | 9 561 |

---

## 19. Section 17 — Fonction de Prédiction Interactive

### Pourquoi une fonction de prédiction ?
C'est un **prototype de service** — une démonstration de ce à quoi ressemblerait le modèle en production.

### Pipeline de la fonction `predict_darija()`

```
Entrée : texte brut en Darija (arabe, latin ou mixte)
    ↓
1. Prétraitement : clean_darija()
    ↓
2. Vectorisation : vec_gs.transform()
    ↓
3. Prédiction : clf_calib.predict_proba()
    ↓
4. Affichage : top 3 classes avec probabilités
```

### Exemples de prédictions testées

**Exemple 1** — Texte en arabe natif :
```
Texte   : كاين ناس مزيان بزاف في المغرب والله
Prédict : Soutien_Encouragement (58.1%)
Top 2   : Opinion (29.7%), Politics_Society (4.3%)
```
*Prédiction correcte mais hésitante — la frontière Soutien ↔ Opinion est floue par nature.*

**Exemple 2** — Darija romanisé, contexte sportif :
```
Texte   : hhhh walakin l match kant mezyan bezzaf
Prédict : Opinion (73.2%)
Top 2   : Sports_Fitness (10.3%), Entertainment (6.9%)
```
*Raisonnable — "mezyan bezzaf" (très bien) domine sur "match". Frontière Opinion ↔ Sports.*

**Exemple 3** — Encouragement religieux :
```
Texte   : Allah y3tik saha u raha, mchiti temsha
Prédict : Soutien_Encouragement (83.7%)
Top 2   : Opinion (2.5%), Religion (2.1%)
```
*Très confiante et correcte — formule d'encouragement figée apprise par le modèle. Distinction correcte Soutien vs Religion.*

### Ce que ces exemples confirment

**La confiance est un signal fiable.** Le modèle est plus sûr quand le texte contient des formules figées et récurrentes ("Allah y3tik saha"), et plus hésitant quand le texte mélange plusieurs dimensions sémantiques.

**Le prétraitement est visible.** Le "hhhh" est converti en "hh" dans le champ "Nettoyé" — sans ce prétraitement, les bruits graphiques du Darija informel fragmenteraient inutilement l'espace des n-grams.

---

## 20. Section 18 — Cross-Validation 5 Plis

### Pourquoi la cross-validation ?
Un seul split train/test peut être chanceux ou malchanceux. La cross-validation donne une évaluation **plus robuste et plus fiable**.

### Fonctionnement — k-Fold Cross-Validation

```
Dataset complet (train set uniquement, 38 241 exemples)
    ┌────┬────┬────┬────┬────┐
    │ F1 │ F2 │ F3 │ F4 │ F5 │
    └────┴────┴────┴────┴────┘

Itération 1 : [TRAIN: F2,F3,F4,F5] → [VALID: F1] → Score F1₁
Itération 2 : [TRAIN: F1,F3,F4,F5] → [VALID: F2] → Score F1₂
Itération 3 : [TRAIN: F1,F2,F4,F5] → [VALID: F3] → Score F1₃
Itération 4 : [TRAIN: F1,F2,F3,F5] → [VALID: F4] → Score F1₄
Itération 5 : [TRAIN: F1,F2,F3,F4] → [VALID: F5] → Score F1₅

Résultat = moyenne(F1₁...F1₅) ± écart-type
```

Chaque exemple est utilisé **une fois** comme validation → résultat plus stable qu'un seul split.

### Les 3 pipelines comparés

| Pipeline | F1 Moyen | F1 Std | Overfit Moy | Temps |
|----------|----------|--------|-------------|-------|
| **SVM + TF-IDF char seul** | **0.5983** | **0.0030** | **+0.349** | 535s |
| SVM + TF-IDF combine | 0.5965 | 0.0033 | +0.393 | 463s |
| LR + TF-IDF combine | 0.5888 | 0.0032 | +0.403 | 1863s |

### Résultats détaillés — SVM + TF-IDF char seul

| Fold | F1 Validation | Overfit |
|------|---------------|---------|
| 1 | 0.5976 | +0.350 |
| 2 | 0.6029 | +0.344 (meilleur) |
| 3 | 0.5968 | +0.351 |
| 4 | 0.5999 | +0.347 |
| 5 | 0.5942 | +0.355 (plus faible) |
| **Écart max-min** | **0.0087** | **→ très stable** |

### Analyse des résultats CV

**La stabilité est excellente** (std = 0.003 sur tous les pipelines) → les résultats ne dépendent pas du hasard du découpage. Le dataset est suffisamment homogène pour que chaque fold soit représentatif.

**SVM + TF-IDF char seul reste le meilleur** malgré l'idée séduisante de combiner word+char. La combinaison ajoute du bruit (orthographe variable en Darija) qui noie partiellement le signal des char n-grams.

**LR est à écarter** : F1 le plus faible (0.5888), overfit le plus fort (+0.403) ET 3.5× plus lent que SVM char seul.

**Conclusion de la CV** : La cross-validation clôt définitivement la phase d'évaluation des modèles classiques. Le plafond F1 ≈ 0.60 est confirmé avec certitude statistique sur 5 découpages indépendants.

---

## 21. Section 19 — FastText Embeddings + SVM Hybride

### Qu'est-ce que FastText ?
FastText est un modèle développé par **Facebook Research** qui apprend des représentations vectorielles (embeddings) pour chaque mot.

**Différence fondamentale avec TF-IDF :**

| Aspect | TF-IDF | FastText |
|--------|--------|----------|
| Type | Vecteur **creux** (99.99% de zéros) | Vecteur **dense** (100 nombres réels) |
| Basé sur | Fréquence des mots | **Contexte** des mots |
| Taille | 100 000+ dimensions | 100 dimensions |
| Variantes orthographiques | "mezyan" ≠ "mzyan" | "mezyan" ≈ "mzyan" |

**Pourquoi FastText est particulièrement adapté à la Darija :** FastText décompose les mots en character n-grams en interne → les mots ayant des sous-chaînes communes auront des embeddings proches. "bzzaf" et "bezzaf" (même mot) auront des vecteurs similaires.

### Paramètres d'entraînement

| Paramètre | Valeur | Signification |
|-----------|--------|---------------|
| `sg=1` | Skip-gram | Prédit les mots contextuels → meilleur pour mots rares |
| `vector_size=100` | 100 dimensions | Chaque mot → 100 nombres |
| `window=5` | 5 mots | Contexte = 5 mots avant/après |
| `min_count=2` | Minimum 2 occurrences | Ignore les mots hapax |
| `epochs=10` | 10 passages | Sur tout le corpus |

### Validation : similarités sémantiques

```python
Similaires à 'mezyan' : [('mzyan', 0.92), ('mzien', 0.89), ...]
```
Les variations orthographiques de la Darija sont bien capturées → confirmation que FastText comprend la morphologie.

### Pipeline Hybride

```
Texte Darija
    │
    ├── TF-IDF char (2,4) ─────── matrice sparse (100k colonnes)
    │                                     │
    └── FastText [moyenne tokens] ─ vecteur dense (100 colonnes)
                                          │
         hstack([sparse, dense]) ─────────┤
                                          ↓
                              SVM calibré (classification)
```

### Résultats FastText

| Pipeline | F1-macro | Accuracy | Overfit | Verdict |
|----------|----------|----------|---------|---------|
| SVM + TF-IDF char seul (référence) | 0.6043 | 0.6335 | +0.336 | Référence |
| SVM FastText only | 0.4977 | 0.5509 | **+0.004** | Généralise mais trop pauvre |
| **SVM Hybride TF + FastText** | **0.6097** | **0.6368** | +0.329 | **Premier dépassement du plafond !** |

### Analyse des résultats

**FastText seul (-0.107 vs TF-IDF)** : Surprenant mais explicable. Les embeddings FastText **moyennent** tous les mots d'un texte en un seul vecteur de 100 dimensions. Cette agrégation par moyenne écrase l'information discriminante. De plus, le corpus de 47 802 textes courts est trop petit pour entraîner des embeddings de qualité.

**Hybride TF + FastText : premier dépassement du plafond 0.604** : La combinaison des deux représentations complémentaires permet de franchir la barrière. Gains notables sur Publicité_Spam (+0.028) et Entertainment (+0.019) — deux classes où la sémantique aide.

---

## 22. Section 20 — DarijaBERT + CLS Embeddings

### Qu'est-ce que BERT ?
BERT (Bidirectional Encoder Representations from Transformers) est un modèle de langage révolutionnaire (Google, 2018) qui produit des **représentations contextuelles** — le même mot a une représentation différente selon son contexte.

```
TF-IDF/FastText : "bank" dans "river bank" = "bank" dans "bank account" → même vecteur
BERT            : "bank" dans "river bank" ≠ "bank" dans "bank account" → vecteurs différents
```

### DarijaBERT : BERT spécialisé pour la Darija
`SI2M-Lab/DarijaBERT` est un BERT **pré-entraîné spécifiquement sur la Darija marocaine** — c'est le modèle de référence pour ce dialecte.

### Stratégie utilisée : Feature Extraction (pas de Fine-Tuning)

On n'entraîne **pas** DarijaBERT (trop coûteux sans GPU). On l'utilise comme un **extracteur de features** :

```
Texte Darija → Tokenisation BERT → [CLS] token → Vecteur 768 dimensions
```

Le token `[CLS]` (Classification) est ajouté au début de chaque texte par BERT. Après l'encodage, sa représentation (768 dimensions) est un **résumé contextuel** du texte entier.

### Contrainte : CPU sans GPU

BERT sur CPU est très lent → travail sur un **échantillon stratifié de 4000 textes** (représentatif) au lieu du dataset complet.

| Paramètre | Valeur | Raison |
|-----------|--------|--------|
| `batch_size=64` | 64 textes à la fois | Compromis mémoire/vitesse |
| `max_length=64` | Tronquer à 64 tokens | Commentaires courts → peu de perte |
| `N_BERT_SAMPLE=4000` | 4000 exemples | Démonstration viable sur CPU |

### Résultats DarijaBERT

| Pipeline | F1-macro | Accuracy | Overfit |
|----------|----------|----------|---------|
| SVM + TF-IDF (38k exemples, référence) | 0.6043 | 0.6335 | +0.336 |
| SVM + DarijaBERT seul (4k) | 0.4645 | 0.4765 | **+0.153** |
| **SVM + TF-IDF + DarijaBERT (4k)** | **0.5517** | **0.5626** | +0.448 |

### Gains et pertes par classe

| Classe | TF-IDF seul | Hybride BERT | Évolution |
|--------|------------|--------------|-----------|
| Entertainment | 0.278 | **0.471** | **+0.193** |
| Publicité_Spam | 0.582 | **0.717** | **+0.135** |
| Religion | 0.725 | 0.717 | -0.008 |
| **Opinion** | 0.496 | **0.139** | **-0.357** |

### Analyse critique

**DarijaBERT sous les performances TF-IDF** s'explique par 3 facteurs :
1. **Volume insuffisant** (2 997 exemples vs 38 241 pour TF-IDF) — BERT a besoin de volume
2. **Agrégation naïve** — vecteur [CLS] utilisé brut, sans fine-tuning
3. **Pas de GPU** — impossible de traiter les 47 802 exemples

**Le gain sur Entertainment (+0.193)** est le résultat le plus précieux. C'est la seule approche ayant vraiment amélioré cette classe — preuve que les embeddings contextuels capturent quelque chose que les n-grams ne voient pas.

**L'effondrement d'Opinion (-0.357)** confirme définitivement que son problème est structurel. BERT n'a pas de "triche" par fréquence — il encode le sens réel. Et le sens d'Opinion est trop vague pour être encodé correctement.

### Conclusion DarijaBERT
Avec le corpus complet et un **fine-tuning de la couche de classification**, DarijaBERT dépasserait très probablement le plafond 0.61 de manière significative. C'est la piste la plus prometteuse, conditionnée à l'accès à un GPU.

---

## 23. Section 21 — Tableau Récapitulatif Complet Toutes Expériences

### Vue d'ensemble du total des expériences

| Catégorie | Nombre | Description |
|-----------|--------|-------------|
| Benchmark individuel | 35 | 5 vectoriseurs × 7 modèles |
| Cross-Validation | 3 | 3 pipelines × 5 folds |
| Ensemble | 4 | Hard/Soft Voting, Stacking, GridSearch |
| FastText | 2 | FastText seul + Hybride |
| DarijaBERT | 2 | DarijaBERT seul + TF-IDF + DarijaBERT |
| **Total** | **~46** | **expériences distinctes** |

### Classement des meilleures expériences

| Rang | Expérience | F1-macro | Type |
|------|-----------|----------|------|
| 🥇 1 | Stacking (SVC+LR+SGD+Ridge) | 0.6207 | Ensemble |
| 🥈 2 | Soft Voting | 0.6123 | Ensemble |
| 🥉 3 | SVM Hybride TF+FastText | 0.6097 | FastText |
| 4 | Linear SVC + TF-IDF char | 0.6043 | Benchmark |
| 5 | SGD + TF-IDF combined | 0.6000 | Benchmark |

---

## 24. Section 22 — Suivi Expérimental avec Weights & Biases (W&B)

### Qu'est-ce que W&B ?
**Weights & Biases** est une plateforme **MLOps** (Machine Learning Operations) qui permet de tracker, visualiser et comparer automatiquement toutes les expériences ML.

> **Analogie :** C'est comme un carnet de laboratoire numérique intelligent — il enregistre automatiquement chaque expérience avec tous ses paramètres et résultats.

### Ce que W&B enregistre pour chaque run

```python
wandb.log({
    'accuracy': 0.634,
    'f1_macro': 0.604,
    'f1_weighted': 0.631,
    'overfit': 0.336
})
```

Avec des **tags** ('benchmark', 'advanced') pour filtrer les expériences dans le dashboard.

### Modes de fonctionnement

| Mode | Usage | Avantage |
|------|-------|----------|
| **Offline** (utilisé ici) | Sauvegarde locale `./wandb/` | Aucun compte nécessaire |
| Online | Dashboard web en temps réel | Visualisation interactive |

### Bilan du tracking
**46 runs loggés** correspondant à toutes les expériences du notebook. Pour synchroniser les runs offline vers le dashboard web : `wandb sync ./wandb/`

**Pourquoi c'est important ?** W&B permet de reproduire n'importe quelle expérience passée et de comparer systématiquement toutes les approches — pratique essentielle en recherche ML professionnelle.

---

## 25. Section 23 — Analyses Complémentaires

### Analyse par type de source

| Source | Accuracy | Nb exemples | Part du corpus |
|--------|----------|-------------|----------------|
| **comment** | 0.897 | 46 877 | **98.1%** |
| **transcription** | 0.976 | 925 | 1.9% |
| **Globale** | **0.898** | 47 802 | 100% |

**Observation** : Le modèle atteint 97.6% d'accuracy sur les transcriptions contre 89.7% sur les commentaires (+7.9 points). Les transcriptions produisent un Darija plus structuré (phrases complètes, orthographe plus régulière). Mais les transcriptions ne représentent que 1.9% du corpus — c'est les commentaires qui définissent réellement le niveau du modèle.

### Analyse par longueur de texte

| Quartile | Accuracy | Nb exemples |
|----------|----------|-------------|
| Très court | 0.893 | 12 027 |
| Court | 0.890 | 12 309 |
| Moyen | 0.897 | 11 520 |
| **Long** | **0.914** | 11 946 |

**Observation** : Écart de seulement +0.024 entre le plus court et le plus long → la longueur n'est pas un facteur critique. Le modèle performe de manière homogène quelle que soit la taille du commentaire — bonne nouvelle pour la robustesse en production.

### Guide de fine-tuning BERT (perspectives)

**Trois modèles recommandés pour aller plus loin :**

| Priorité | Modèle | Pourquoi |
|----------|--------|----------|
| 1 | **DarijaBERT** (SI2M-Lab) | Pré-entraîné sur la Darija marocaine |
| 2 | **AraBERT v2** (aubmindlab) | Pré-entraîné sur l'arabe dialectal large |
| 3 | **XLM-RoBERTa** (meta) | Modèle multilingue généraliste robuste |

**Code de référence pour le fine-tuning (nécessite GPU) :**

```python
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer

model = AutoModelForSequenceClassification.from_pretrained(
    'SI2M-Lab/DarijaBERT', num_labels=12)

training_args = TrainingArguments(
    output_dir='./darijabert_finetuned',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    evaluation_strategy='epoch',
    report_to='wandb')
```

Gains attendus avec fine-tuning : **+5 à +15 points de F1** sur des tâches similaires en NLP dialectal.

---

## 26. Section 24 — Rapport HTML Exportable

### Ce que le rapport HTML contient

Un fichier HTML autonome (`rapport_nlp_darija_v4.html`) intégrant :
- **6 KPIs** (Key Performance Indicators) : métriques clés en gros chiffres
- **Champion** : meilleure combinaison identifiée
- **14 visualisations** intégrées en base64 directement dans le HTML (pas de fichiers séparés)
- **Style publication** : design professionnel adapté à une présentation ou article

**Avantage :** Le fichier peut être ouvert dans n'importe quel navigateur, partagé par email, ou hébergé sur un site web — sans avoir besoin de Jupyter Notebook.

---

## 27. Section 25 — Synthèse et Conclusions Générales

### Récapitulatif des décisions clés

| Décision | Choix fait | Raison |
|----------|-----------|--------|
| Métrique principale | F1-macro | Dataset déséquilibré (ratio 12:1) |
| Prétraitement | Léger et ciblé | Préserver le code-switching Darija |
| Meilleure vectorisation | TF-IDF char (2,4-grams) | Robuste aux fautes d'orthographe |
| Évaluation | Cross-validation 5 plis | Plus robuste qu'un seul split |
| Meilleur modèle individuel | Linear SVC | Optimise la marge, idéal haute dimension |
| Meilleure stratégie globale | Stacking (F1=0.621) | Méta-apprentissage entre modèles |
| Tracking | Weights & Biases | Traçabilité et reproductibilité |

### Bilan chiffré global final

| Indicateur | Valeur |
|------------|--------|
| Exemples total | 47 802 (38 241 train / 9 561 test) |
| Classes | 12 |
| Combinaisons testées | 35 |
| Expériences totales | ~46 |
| Meilleur F1-macro (individuel) | **0.604** — Linear SVC + TF-IDF char 2-4grams |
| Meilleur F1-macro (ensemble) | **0.621** — Stacking |
| Accuracy maximale | **0.641** — Stacking |
| Confiance moyenne du modèle | 0.674 |
| Accuracy à seuil 0.90 | 0.895 sur 24% des prédictions |
| Accuracy à seuil 0.95 | 0.929 sur 15.7% des prédictions |

### Pourquoi le plafond F1 ≈ 0.60 ?

Les approches classiques TF-IDF + classifieurs linéaires ont atteint leur **plafond naturel** autour de F1 = 0.60-0.62. Ce plafond n'est pas dû à un mauvais choix de modèle ou d'hyperparamètres, mais à deux limites fondamentales :

1. **La représentation de surface** : Les n-grams de caractères capturent les motifs orthographiques mais pas la **sémantique** — ils ne comprennent pas le "sens" d'un texte.

2. **La qualité du schéma d'annotation** : Les classes Opinion, Entertainment et Inclassable_Bruit ont des frontières floues. Aucun algorithme, aussi puissant soit-il, ne peut discriminer ce qui n'est pas discriminable au niveau des caractères.

### Ce qu'on a appris sur la Darija

1. **Le code-switching** (arabe + latin) est une caractéristique fondamentale → nécessite des approches multilingues
2. **Les char n-grams** (2-4) sont plus robustes que les word n-grams pour la Darija à cause des variations orthographiques
3. **DarijaBERT** est le modèle de référence pour cette langue — preuve que les modèles pré-entraînés spécialisés surpassent les approches génériques
4. **La classe Opinion** est la limitation principale du schéma d'annotation — elle se comporte comme une "poubelle" qui capte tout ce qui n'est pas clairement autre chose

### Ce qu'on a appris sur le Pipeline ML

1. **L'EDA** → toujours commencer par comprendre les données (déséquilibres, distributions, qualité)
2. **Le benchmark systématique** → ne jamais supposer quel modèle est le meilleur sans tester
3. **Le F1-macro** → la bonne métrique pour les données déséquilibrées
4. **La cross-validation** → l'évaluation robuste est non-négociable en recherche
5. **L'interprétabilité** → toujours analyser les erreurs et les features importantes
6. **La confiance** → le modèle sait quand il se trompe, c'est exploitable en production

### Perspectives d'amélioration

**Court terme (faisable):**
- Réduire C pour diminuer l'overfitting
- Augmentation de données pour les classes minoritaires (Entertainment, Publicité_Spam)

**Moyen terme (nécessite des ressources) :**
- **Fine-tuning complet de DarijaBERT** sur GPU → gain attendu +5 à +10 points F1
- Réviser les exemples incorrectement annotés de la classe Opinion

**Long terme (recherche) :**
- Publication du corpus sur Hugging Face Datasets avec licence CC BY 4.0
- Déploiement en API FastAPI + interface web pour usage en production
- Augmentation vers 150 000+ exemples pour repousser le plafond

---

## 📌 Points Clés à Retenir pour l'Oral

1. **La Darija est difficile** parce qu'elle mélange plusieurs langues, n'a pas d'orthographe standardisée, et les ressources NLP spécialisées sont rares.

2. **Le meilleur vectoriseur est TF-IDF char 2-4grams** — les n-grams de caractères sont robustes aux variations orthographiques de la Darija.

3. **Le meilleur modèle individuel est Linear SVC** avec F1=0.604 — le plafond des approches TF-IDF classiques.

4. **On utilise le F1-macro** (pas l'accuracy) à cause du déséquilibre des classes (ratio 12:1).

5. **L'overfit est structural** : le modèle mémorise (~F1 train=0.98) mais généralise modérément (~F1 test=0.60) — c'est une propriété des approches TF-IDF sur langues peu dotées.

6. **La confiance est exploitable en production** : avec un seuil 0.80, on atteint 85% d'accuracy sur 36% des cas.

7. **DarijaBERT est la prochaine étape** — les embeddings contextuels sont nécessaires pour dépasser le plafond 0.62, notamment sur les classes difficiles (Entertainment +0.193 avec DarijaBERT).

8. **W&B assure la traçabilité** — toutes les ~46 expériences sont loggées et comparables.

---

*Document généré depuis le notebook `Etape4_Classification_Darija_ANNOTE.ipynb` — Version annotée et expliquée complète.*
