# Sentinel Senior

Systeme de suivi, detection et prevention de la fragilite motrice chez les personnes du troisieme age.

## Fonctionnalites

- **Gestion des patients** : Enregistrement et suivi des dossiers
- **Evaluations** : Tests fonctionnels et calcul du score de fragilite (criteres de Fried)
- **Detection automatique** : Alertes en cas de deterioration
- **Tableau de bord** : Visualisation cardiaque et indicateurs de sante
- **API REST** : Endpoints pour l'integration

## Installation

### Prerequis

- Python 3.8+
- pip

### Etapes

```bash
# Creer l'environnement virtuel
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Installer les dependances
pip install -r requirements.txt

# Lancer l'application
python run.py
```

L'application sera accessible a : `http://localhost:5000`

## Structure du projet

```
Sentinel_Senior/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── api.py
│   ├── detection.py
│   ├── static/images/    # Image coeur : coeur.png ou coeur.jpg
│   └── templates/
├── run.py
├── requirements.txt
└── README.md
```

## API

- `GET /api/patients` - Liste des patients
- `POST /api/patients` - Creer un patient
- `GET /api/patients/<id>/evaluations` - Evaluations d'un patient
- `POST /api/patients/<id>/evaluations` - Nouvelle evaluation
- `GET /api/alertes/non-traitees` - Alertes en attente
- `GET /api/statistiques/globales` - Statistiques

## Image du coeur

Placez l'image du coeur dans : `app/static/images/coeur.png` ou `coeur.jpg`

## Licence

Projet de memoire universitaire.
