# Sentinel Senior - Système de Suivi de Fragilité Motrice

Système complet de suivi, détection et prévention de la fragilité motrice chez les personnes du troisième âge.

## Fonctionnalités

### 1. Gestion des Patients
- Enregistrement et suivi des patients
- Dossiers médicaux complets
- Historique des évaluations

### 2. Évaluations de Fragilité
- Tests fonctionnels (vitesse de marche, force de préhension, équilibre, etc.)
- Calcul automatique du score de fragilité basé sur les critères de Fried
- Classification automatique : Normal, Pré-fragile, Fragile, Très fragile
- Génération automatique de recommandations personnalisées

### 3. Détection Automatique
- Détection de détérioration des capacités motrices
- Comparaison des évaluations successives
- Génération automatique d'alertes selon les seuils critiques

### 4. Système d'Alertes
- Alertes prioritaires (faible, moyen, élevé, critique)
- Suivi du traitement des alertes
- Notifications pour les détériorations détectées

### 5. Statistiques et Visualisations
- Tableau de bord avec statistiques globales
- Graphiques de répartition par niveau de fragilité
- Évolution temporelle des évaluations
- Analyses des tendances

## Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**

2. **Créer un environnement virtuel (recommandé)**
```bash
python -m venv venv
```

3. **Activer l'environnement virtuel**
   - Sur Windows:
   ```bash
   venv\Scripts\activate
   ```
   - Sur Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

5. **Initialiser la base de données**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Utilisation

### Démarrer l'application

```bash
python run.py
```

L'application sera accessible à l'adresse: `http://localhost:5000`

### Structure de l'API REST

#### Patients
- `GET /api/patients` - Liste tous les patients
- `GET /api/patients/<id>` - Détails d'un patient
- `POST /api/patients` - Créer un nouveau patient
- `PUT /api/patients/<id>` - Mettre à jour un patient
- `DELETE /api/patients/<id>` - Désactiver un patient

#### Évaluations
- `GET /api/evaluations` - Liste toutes les évaluations
- `GET /api/patients/<id>/evaluations` - Évaluations d'un patient
- `POST /api/patients/<id>/evaluations` - Créer une évaluation
- `GET /api/evaluations/<id>` - Détails d'une évaluation

#### Mesures Motrices
- `GET /api/patients/<id>/mesures` - Mesures d'un patient
- `POST /api/patients/<id>/mesures` - Enregistrer une mesure

#### Alertes
- `GET /api/alertes/non-traitees` - Alertes non traitées
- `GET /api/patients/<id>/alertes` - Alertes d'un patient
- `PUT /api/alertes/<id>` - Traiter une alerte

#### Statistiques
- `GET /api/statistiques/globales` - Statistiques globales
- `GET /api/patients/<id>/statistiques` - Statistiques d'un patient

## Critères de Fragilité (Fried)

Le système utilise les 5 critères de Fried pour évaluer la fragilité:

1. **Perte de poids involontaire** (> 5% en 1 an)
2. **Fatigue/Épuisement** (auto-rapporté)
3. **Activité physique réduite**
4. **Lenteur de marche** (< 0.8 m/s)
5. **Faiblesse musculaire** (force de préhension réduite)

**Classification:**
- **Normal**: 0 critère
- **Pré-fragile**: 1-2 critères
- **Fragile**: 3 critères
- **Très fragile**: 4-5 critères

## Structure du Projet

```
Sentinel_Senior/
├── app/
│   ├── __init__.py          # Configuration Flask et initialisation
│   ├── models.py             # Modèles de base de données
│   ├── routes.py             # Routes principales (pages web)
│   ├── api.py                # API REST
│   ├── detection.py          # Algorithmes de détection
│   └── templates/            # Templates HTML
│       ├── index.html
│       ├── patients.html
│       ├── evaluations.html
│       ├── alertes.html
│       └── statistiques.html
├── run.py                    # Point d'entrée de l'application
├── requirements.txt          # Dépendances Python
└── README.md                 # Ce fichier
```

## Technologies Utilisées

- **Backend**: Flask (Python)
- **Base de données**: SQLite (développement) / SQLAlchemy ORM
- **Frontend**: Bootstrap 5, Chart.js
- **API**: REST API avec Flask

## Notes de Développement

- La base de données SQLite est créée automatiquement au premier lancement
- Pour la production, configurez une base de données PostgreSQL ou MySQL
- Modifiez `SECRET_KEY` dans `app/__init__.py` pour la production
- Les migrations de base de données sont gérées par Flask-Migrate

## Auteur

Projet de mémoire - Système de suivi de fragilité motrice

## Licence

Ce projet est développé dans le cadre d'un mémoire universitaire.
