# Cahier des charges du projet 2

## Classification automatique de textes en Darija marocaine

**Constitution et annotation semi-automatique d’un corpus de 25 000 textes à partir de sources hétérogènes**

---

## 1. Contexte général

La **Darija marocaine** (arabe dialectal marocain) est aujourd’hui massivement utilisée dans les échanges numériques : commentaires sur les plateformes vidéo, réseaux sociaux, forums et espaces communautaires. Malgré cette forte présence, la Darija reste une **langue faiblement dotée en ressources linguistiques annotées**, ce qui limite le développement de modèles de Traitement Automatique du Langage Naturel (NLP) performants.

La classification automatique de textes en Darija constitue ainsi un **enjeu scientifique, pédagogique et industriel**, notamment pour :

- la veille sociale et médiatique,
- la modération de contenu,
- l’analyse thématique,
- les assistants conversationnels et chatbots.

Ce projet vise à confronter les étudiants à un **cas réel de NLP pour langue low-resource**, en mettant l’accent sur la **constitution d’un dataset annoté de grande taille (15 000 textes)**, via une **labellisation semi-automatique assistée par LLM**, et sur l’analyse de l’impact des **sources et de la longueur des textes** sur les performances des modèles.

---

## 2. Objectifs du projet

### 2.1 Objectifs pédagogiques

À l’issue du projet, l’étudiant devra être capable de :

- collecter des données textuelles réelles en Darija à partir de sources publiques ;
- comprendre et gérer les spécificités linguistiques de la Darija (absence de normalisation, code-switching, Arabizi) ;
- concevoir une pipeline NLP complète et reproductible ;
- mettre en œuvre une stratégie de **labellisation semi-automatique à grande échelle** ;
- annoter et valider un corpus de **15 000 textes** ;
- entraîner et comparer plusieurs classifieurs de texte ;
- analyser de manière critique les résultats expérimentaux.

### 2.2 Compétences visées

- NLP appliqué aux langues peu dotées  
- Machine Learning supervisé  
- Data annotation à grande échelle  
- MLOps léger (tracking expérimental)  
- Analyse critique des biais linguistiques et algorithmiques  

---

## 3. Périmètre et contraintes

- Projet réalisé en **binôme ou trinôme**
- Langage principal : **Python**
- Langue cible : **Darija marocaine**
- Taille du dataset final : **15 000 textes annotés**
- Utilisation obligatoire :
  - d’une labellisation semi-automatique (LLM + validation humaine),
  - d’un outil de suivi expérimental (MLflow ou Weights & Biases).
- Documentation complète exigée (rapport + code).

---

## 4. Tâche de classification

### 4.1 Nature de la tâche

La tâche consiste à attribuer à chaque texte en Darija **une seule classe**, définie par l’enseignant ou le groupe, par exemple :

- classification thématique (actualité, sport, religion, divertissement, etc.) ;
- classification d’intention (question, opinion, information, plainte, etc.) ;
- classification de type de message.

Le choix des classes doit être :

- cohérent avec les données collectées ;
- clairement défini et justifié dans le rapport.

---

## 5. Sources de données et répartition (25 000 textes)

Les données doivent provenir **exclusivement de sources publiques** en Darija marocaine, principalement issues de **contenus vidéo et de leurs interactions sociales**.  
Les étudiants devront exploiter **Instagram et YouTube** comme sources principales, en combinant :

- les **commentaires** des publications / vidéos ;

- la **transcription automatique des vidéos YouTube** (speech-to-text).

L’objectif est de constituer un corpus riche, varié et représentatif de la Darija **orale et écrite**, telle qu’utilisée dans des contextes réels.

 == Les étudiants sont encouragés à rechercher ces influenceurs sur **YouTube** lorsqu’ils existent également sur cette plateforme.

### **Sources**

**Medical / Santé**

- dr.abderrahimznt

- dr_siham_mansouri

**Business / Économie**

- youssefakalal

- hamzaboulfeth

**Sports / Fitness**

- ingenieur.fitness

- equipedumaroc

**Politics / Société**

- achraf_belmoudden

- younes.ftaite

**Religion**

- مصطفى الهلالي

- سعيد الكملي

- فريد الانصاري

**Entertainment / Divertissement**

- ezzoubairhilal

- bahae.sanari

**Food / Cuisine**

- cuisine_halima__filali

- mehdi_tastediscovery

**Miscill (contenu mixte)**

- hesspress

### 5.2 Champ *Miscill*

Les sources *Miscill* produisent des contenus pouvant appartenir à **plusieurs domaines thématiques** (santé, politique, religion, etc.).

Il revient aux étudiants de :

- sélectionner manuellement les vidéos pertinentes ;

- analyser chaque texte (commentaire ou transcription) ;

- **reclasser chaque instance dans l’une des classes définies du projet** ;

- justifier ces décisions dans le rapport.

---

### 5.3 Types de données à collecter

Pour chaque source :

1. **Commentaires**
   
   - commentaires Instagram (posts et reels) ;
   
   - commentaires YouTube (vidéos).

2. **Transcriptions YouTube**
   
   - transcription automatique des vidéos ;
   
   - conservation de la Darija orale telle quelle.

Chaque entrée du dataset doit inclure :

- identifiant unique ;

- texte brut original ;

- type de source (*Instagram comment*, *YouTube comment*, *YouTube transcription*) ;

- classe finale.

---

## 6. Étape 1 – Extraction des données

### 6.1 Données à collecter

Pour chaque texte :

- identifiant unique ;
- texte brut (orthographe originale conservée) ;
- source (YouTube, Instagram, Transcription) ;
- date (optionnelle).

### 6.2 Stockage

- Format structuré : CSV ou JSON
- Encodage UTF-8
- Une colonne dédiée à la langue (Darija)

---

## 7. Étape 2 – Prétraitement et exploration des données

### 7.1 Spécificités linguistiques de la Darija

Les étudiants devront prendre en compte :

- absence de normalisation orthographique ;
- mélange Darija / arabe standard / français ;
- écriture en alphabet arabe et/ou latin ;
- usage de chiffres (Arabizi).

### 7.2 Prétraitement obligatoire

- nettoyage léger (URLs, emojis, spam) ;
- normalisation partielle (optionnelle et justifiée) ;
- **éviter le sur-nettoyage** afin de préserver la richesse linguistique.

### 7.3 Analyse exploratoire

- longueur moyenne des textes par source ;
- distribution des caractères (arabe / latin) ;
- mots et n-grammes fréquents ;
- détection du code-switching.

---

## 8. Étape 3 – Labellisation semi-automatique (étape centrale)

### 8.1 Objectif

Annoter **25 000 textes en Darija** en combinant :

- pré-annotation automatique par un LLM ;
- validation et correction humaines ciblées ;
- contrôle qualité systématique.

---

### 8.2 Démarche recommandée de labellisation

#### Étape 1 – Annotation manuelle de référence

- Sélectionner **1 000 à 2 000 textes**.
- Annotation 100 % manuelle.
- Élaboration d’un **guide d’annotation**.
- Constitution d’un **gold standard partiel**.

---

#### Étape 2 – Pré-annotation automatique par LLM

- Utiliser un LLM capable de traiter la Darija.
- Contraindre la sortie à une seule classe.
- Tester plusieurs stratégies de prompt (zero-shot, few-shot).

---

#### Étape 3 – Annotation assistée avec Label Studio

Les données doivent être importées dans  
**Label Studio**.

Fonctionnement attendu :

- affichage du texte brut ;
- affichage du label proposé par le LLM ;
- validation, correction ou rejet par l’annotateur humain.

---

#### Étape 4 – Contrôle qualité et équilibrage

Les étudiants devront :

- mesurer le taux de correction des labels automatiques ;
- analyser les erreurs spécifiques à la Darija ;
- équilibrer le dataset final entre les classes.

---

## 9. Étape 4 – Entraînement et évaluation des modèles

### 9.1 Modèles requis (minimum)

- Logistic Regression  
- Naive Bayes  
- Support Vector Machine (SVM)

### 9.2 Représentations textuelles

- Bag-of-Words  
- TF-IDF  
- Character n-grams (fortement recommandé)  
- Embeddings (optionnel)

### 9.3 Métriques d’évaluation

- Accuracy  
- Precision  
- Recall  
- F1-score  
- Matrice de confusion  

---

## 10. Étape 5 – Suivi expérimental (obligatoire)

Les expérimentations doivent être tracées à l’aide de :

- **MLflow** ou
- **Weights & Biases**.

Chaque run doit inclure :

- version du dataset ;
- paramètres du modèle ;
- métriques ;
- artefacts (modèles, graphiques).

---

## 11. Livrables attendus

1. Dataset annoté final de **25 000 textes en Darija**
2. Rapport technique détaillé
3. Code source structuré et documenté
4. Dashboard de tracking expérimental
5. Présentation orale (10–15 minutes)

---

## 12. Critères d’évaluation (indicatif)

| Critère                          | Pondération |
| -------------------------------- | ----------- |
| Qualité du dataset et annotation | 50 %        |
| Pipeline NLP                     | 10 %        |
| Modélisation et évaluation       | 10 %        |
| Tracking et reproductibilité     | 10 %        |
| Analyse critique                 | 15 %        |

---

## 13. Extensions possibles (bonus)

- Étude comparative par source (Wikipedia vs réseaux sociaux)
- Analyse de l’impact de la longueur des textes
- Fine-tuning d’un modèle multilingue
- Publication du corpus (open science)

---

### 14. Section — Filtrage linguistique : Darija vs Arabe standard

### Objectif

Cette section vise à définir **les critères de sélection des textes en Darija marocain**, ainsi que **les textes à exclure**, afin d’assurer la cohérence linguistique du dataset final.

L’objectif n’est **pas** de détecter l’arabe en général, mais de :

- **conserver les textes majoritairement en Darija** (écrite en arabe, en latin ou mixte),

- **exclure les textes dominés par l’arabe standard (MSA)** ou non exploitables pour l’analyse de sentiment en Darija.

### Règles générales

#### Textes à **garder**

- Darija écrite :
  
  - en **alphabet latin** (7, 9, 3, etc.)
  
  - en **alphabet arabe**
  
  - en **forme mixte** (arabe + latin)

- Présence de :
  
  - vocabulaire dialectal marocain ;
  
  - structures orales / familières ;
  
  - fautes volontaires, allongements, répétitions (typique des réseaux sociaux).

#### Textes à **éviter**

- Textes rédigés majoritairement en **arabe standard (MSA)** :
  
  - style formel ;
  
  - vocabulaire journalistique, religieux ou institutionnel.

- Commentaires **sans contenu linguistique exploitable** :
  
  - uniquement des emojis ;
  
  - mots trop génériques sans opinion claire.

| Texte                                                                                                                                                             | Décision |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| سلام دكتوره انا وجهي فيه حبوب بزاف رقيق وغليظ وجهي دهني بزاف والى غسلتو بصابون كيرجع ناشف وكيحكني وجهي بزاااف مسامات واسعين ولون مموحدش عطيني حل الله يرحم والديك | À garder |
| Mskine ta7 mn sta7                                                                                                                                                | À garder |
| Hadi 7El9a zwina                                                                                                                                                  | À garder |
| هادي خاسها فيديو آخر للناس اللي مكيقراوش                                                                                                                          | À garder |
| ياله كنت شاد سلسلة تاعك ونشدو بها رمضان بينما وصلتي مليون                                                                                                         | À garder |
| صحافيان فالمستوى نقاش هادف و مفهوم حوار مشوق وغير ممل هذه هي الصحافة لخاصانا فبلادنا                                                                              | À garder |
| يجب استقالة جميع الأحزاب السياسية في المغرب. نقطة عودة إلى السطر                                                                                                  | À éviter |
| خويا خاص هؤلاء المتضاهرين السلميين يتعاونوا مع رجال الامن والقبض على المخربين وتسليمهم لالسلطات                                                                   | À éviter |
| 👏👏👏👏👏👏                                                                                                                                                      | À éviter |
| فنان بما تحمله الكلمة                                                                                                                                             | À éviter |
