# Plan de projet — Probabilité de cyanobactéries, appliquée au lac de Neuchâtel

**Approche** : entraîner un modèle simple sur un grand jeu de données de lacs (USA), en n'utilisant que des variables **transposables** (mois + température), puis l'appliquer au lac de Neuchâtel pour produire une **probabilité par mois** et une carte.

**Durée réaliste** : ~1 à 2 semaines à temps partiel.

**Modèle** : régression logistique (sortie = probabilité), comparée à une Random Forest.

---

## Principe en une phrase

On apprend *quand* les cyanobactéries prolifèrent (chaleur + saison) sur beaucoup de lacs, puis on demande au modèle : « pour les conditions de Neuchâtel chaque mois, quelle est la probabilité ? »

---

## Les données

**1. Jeu d'entraînement — Tick Tick Bloom (DrivenData)**
- Inscription gratuite sur DrivenData pour télécharger les fichiers.
- Fichiers utiles uniquement :
  - `metadata.csv` : `uid`, `date` (YYYY-MM-DD), `latitude`, `longitude`, `region`
  - `train_labels.csv` : `uid`, `severity` (1 à 5), `density` (cellules/mL)
- **On ignore complètement la partie imagerie satellite** (lourde et hors périmètre). On ne garde que le tabulaire.

**2. Météo — Open-Meteo (Historical Weather API)**
- Gratuit, sans clé d'API. Permet de récupérer la température (et le vent/précipitations si voulu) pour une latitude/longitude/date données.
- Sert à enrichir chaque ligne d'entraînement avec sa température, et à fournir les conditions de Neuchâtel pour l'application.

---

## La cible (binaire)

`severity` va de 1 à 5. On la **binarise** pour la régression logistique :
- ex. `severity >= 4` → `1` (« bloom marqué »), sinon `0`.
- Le choix du seuil doit être justifié dans le rapport (et vous pouvez tester sa sensibilité).

Le modèle sort alors une **probabilité de bloom marqué** entre 0 et 1.

---

## Les variables — et LE piège à éviter

**Variables à utiliser (transposables d'un lac à l'autre) :**
- **Mois** encodé en cyclique (`sin`/`cos`) — votre axe « probabilité par mois ».
- **Température** du jour, et idéalement une moyenne sur les ~7–14 jours précédents (les blooms suivent les vagues de chaleur).
- Optionnel : vent, précipitations récentes.

**⚠️ À NE PAS utiliser comme variables prédictives : la latitude et la longitude.**
> C'est le piège central de la Route 2. Les coordonnées suisses (≈ 47° N, 7° E) sont **totalement hors de la plage des données américaines**. Si le modèle apprend sur les coordonnées, il extrapolera n'importe comment une fois appliqué à Neuchâtel. On s'appuie donc sur des **facteurs physiques** (température, saison) qui, eux, ont le même sens partout.

---

## Workflow condensé

1. **Cadrage + récupération des données** (1–2 j) : inscription DrivenData, téléchargement des 2 CSV, init Git.
2. **Construction du tableau** (1–2 j) : jointure `metadata` + `labels` sur `uid`, puis ajout de la température via Open-Meteo pour chaque (lat, lon, date). Binarisation de la cible.
3. **EDA** (1 j) : distributions, valeurs manquantes, **taux de la classe positive** (déséquilibre), lien température/saison ↔ bloom.
4. **Modélisation + évaluation** (2–3 j) :
   - Régression logistique avec `class_weight='balanced'`, puis Random Forest en comparaison.
   - **Split temporel** (entraîner sur les années anciennes, tester sur les récentes), pas aléatoire.
   - Métriques : **ROC-AUC** et **PR-AUC**, matrice de confusion, rappel sur la classe positive.
   - Interprétation : signe et poids des coefficients (l'effet de la température doit ressortir).
5. **Application au lac de Neuchâtel + carte** (2–3 j) : voir section ci-dessous.
6. **Restitution** (1–2 j) : README + court rapport.

---

## L'application au lac de Neuchâtel

**A. Le cœur robuste — la probabilité par mois**
- Récupérer, via Open-Meteo, la température mensuelle typique au lac de Neuchâtel.
- Donner ces conditions au modèle pour chaque mois → **12 probabilités** → une courbe annuelle.
- C'est exactement votre idée de départ, et c'est la partie la plus solide du projet (transfert thermique/saisonnier qui a du sens physique).

**B. La carte (heatmap)**
- **Version simple et honnête** : colorer le lac selon la probabilité du mois choisi, et faire évoluer la carte mois par mois (animation temporelle). La probabilité est la même sur tout le lac pour un mois donné.
- **Version enrichie (optionnelle)** : moduler la probabilité par un facteur de risque spatial — les **zones peu profondes et stagnantes** (baies, embouchures) sont plus à risque, ce que confirment les autorités cantonales. À définir à la main par zones, ou via une carte bathymétrique, et à présenter **explicitement comme une pondération heuristique**, pas comme une prédiction apprise.
- Outil : `folium` pour une carte interactive.

---

## Structure de dépôt (légère)

```
projet-cyanobacteries-neuchatel/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                 # metadata.csv, train_labels.csv
│   └── processed/           # tableau final enrichi (météo + cible binaire)
├── notebooks/
│   └── analyse.ipynb        # EDA → modèle → évaluation → application Neuchâtel
└── figures/                 # courbe mensuelle, métriques, heatmap
```

---

## Outils

- **Données** : pandas, requests (appels Open-Meteo)
- **ML** : scikit-learn (régression logistique + Random Forest)
- **Visualisation** : matplotlib (courbe, métriques), folium (carte)
- **Reproductibilité** : Git, `requirements.txt`, seeds fixés

---

## Honnêteté méthodologique (la section qui fait « académique »)

À écrire noir sur blanc dans le rapport — c'est ce qui distingue un bon travail :

- Le **transfert géographique USA → Suisse** est une *démonstration*, pas une prédiction validée sur Neuchâtel. Une vraie validation exigerait des données locales étiquetées, qui n'existent pas sous forme exploitable.
- Le modèle capte surtout le **signal saisonnier et thermique** ; la variation spatiale fine à l'intérieur du lac n'est pas apprise (d'où la pondération heuristique optionnelle).
- Le modèle est **volontairement simple et interprétable** (peu de variables) ; on assume ce choix.
- L'évaluation utilise des **métriques adaptées au déséquilibre** des classes.

> Discuter ces limites n'affaiblit pas le projet : au contraire, c'est la marque d'une démarche rigoureuse.
