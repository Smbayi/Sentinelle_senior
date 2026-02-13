from app import db
from datetime import datetime
from sqlalchemy import Float, Integer, String, DateTime, Text, Boolean

class Patient(db.Model):
    """Modèle pour les patients (personnes du 3ème âge)"""
    __tablename__ = 'patients'
    
    id = db.Column(Integer, primary_key=True)
    nom = db.Column(String(100), nullable=False)
    prenom = db.Column(String(100), nullable=False)
    date_naissance = db.Column(DateTime, nullable=False)
    sexe = db.Column(String(10), nullable=False)  # 'M' ou 'F'
    telephone = db.Column(String(20))
    adresse = db.Column(Text)
    date_inscription = db.Column(DateTime, default=datetime.utcnow)
    notes_medicales = db.Column(Text)
    actif = db.Column(Boolean, default=True)
    
    # Relations
    evaluations = db.relationship('Evaluation', backref='patient', lazy=True, cascade='all, delete-orphan')
    mesures = db.relationship('MesureMotrice', backref='patient', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Patient {self.prenom} {self.nom}>'
    
    def age(self):
        """Calculer l'âge du patient"""
        today = datetime.now()
        return today.year - self.date_naissance.year - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'date_naissance': self.date_naissance.isoformat() if self.date_naissance else None,
            'age': self.age(),
            'sexe': self.sexe,
            'telephone': self.telephone,
            'adresse': self.adresse,
            'date_inscription': self.date_inscription.isoformat() if self.date_inscription else None,
            'notes_medicales': self.notes_medicales,
            'actif': self.actif
        }


class Evaluation(db.Model):
    """Modèle pour les évaluations de fragilité motrice"""
    __tablename__ = 'evaluations'
    
    id = db.Column(Integer, primary_key=True)
    patient_id = db.Column(Integer, db.ForeignKey('patients.id'), nullable=False)
    date_evaluation = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Scores d'évaluation
    score_fragilite = db.Column(Float)  # Score global de fragilité (0-100)
    niveau_fragilite = db.Column(String(20))  # 'Normal', 'Pré-fragile', 'Fragile', 'Très fragile'
    
    # Tests fonctionnels
    vitesse_marche = db.Column(Float)  # m/s
    force_prehension = db.Column(Float)  # kg
    equilibre_statique = db.Column(Float)  # secondes
    test_leve_chaise = db.Column(Float)  # secondes (5 fois)
    
    # Indicateurs de fragilité
    perte_poids = db.Column(Boolean, default=False)
    fatigue = db.Column(Boolean, default=False)
    activite_physique_reduite = db.Column(Boolean, default=False)
    lenteur_marche = db.Column(Boolean, default=False)
    faiblesse = db.Column(Boolean, default=False)
    
    # Observations
    observations = db.Column(Text)
    recommandations = db.Column(Text)
    evaluateur = db.Column(String(100))
    
    def __repr__(self):
        return f'<Evaluation {self.id} - Patient {self.patient_id}>'
    
    def calculer_score_fragilite(self):
        """Calculer le score de fragilité basé sur les critères de Fried"""
        criteres = 0
        
        if self.perte_poids:
            criteres += 1
        if self.fatigue:
            criteres += 1
        if self.activite_physique_reduite:
            criteres += 1
        if self.lenteur_marche:
            criteres += 1
        if self.faiblesse:
            criteres += 1
        
        # Score de 0 à 100 (0 = normal, 100 = très fragile)
        self.score_fragilite = (criteres / 5) * 100
        
        # Déterminer le niveau
        if criteres == 0:
            self.niveau_fragilite = 'Normal'
        elif criteres == 1 or criteres == 2:
            self.niveau_fragilite = 'Pré-fragile'
        elif criteres == 3:
            self.niveau_fragilite = 'Fragile'
        else:
            self.niveau_fragilite = 'Très fragile'
        
        return self.score_fragilite
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date_evaluation': self.date_evaluation.isoformat() if self.date_evaluation else None,
            'score_fragilite': self.score_fragilite,
            'niveau_fragilite': self.niveau_fragilite,
            'vitesse_marche': self.vitesse_marche,
            'force_prehension': self.force_prehension,
            'equilibre_statique': self.equilibre_statique,
            'test_leve_chaise': self.test_leve_chaise,
            'perte_poids': self.perte_poids,
            'fatigue': self.fatigue,
            'activite_physique_reduite': self.activite_physique_reduite,
            'lenteur_marche': self.lenteur_marche,
            'faiblesse': self.faiblesse,
            'observations': self.observations,
            'recommandations': self.recommandations,
            'evaluateur': self.evaluateur
        }


class MesureMotrice(db.Model):
    """Modèle pour les mesures motrices continues (capteurs, etc.)"""
    __tablename__ = 'mesures_motrices'
    
    id = db.Column(Integer, primary_key=True)
    patient_id = db.Column(Integer, db.ForeignKey('patients.id'), nullable=False)
    date_mesure = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Types de mesures
    type_mesure = db.Column(String(50), nullable=False)  # 'vitesse', 'equilibre', 'force', 'activite'
    
    # Valeurs de mesure
    valeur = db.Column(Float, nullable=False)
    unite = db.Column(String(20))  # 'm/s', 'kg', 'secondes', 'pas/jour'
    
    # Métadonnées
    source = db.Column(String(50))  # 'capteur', 'test_manuel', 'questionnaire'
    notes = db.Column(Text)
    
    def __repr__(self):
        return f'<MesureMotrice {self.type_mesure} - {self.valeur}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date_mesure': self.date_mesure.isoformat() if self.date_mesure else None,
            'type_mesure': self.type_mesure,
            'valeur': self.valeur,
            'unite': self.unite,
            'source': self.source,
            'notes': self.notes
        }


class Alerte(db.Model):
    """Modèle pour les alertes de détection de fragilité"""
    __tablename__ = 'alertes'
    
    id = db.Column(Integer, primary_key=True)
    patient_id = db.Column(Integer, db.ForeignKey('patients.id'), nullable=False)
    date_alerte = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    
    type_alerte = db.Column(String(50), nullable=False)  # 'deterioration', 'chute', 'fragilite_accrue'
    niveau = db.Column(String(20), nullable=False)  # 'faible', 'moyen', 'eleve', 'critique'
    message = db.Column(Text, nullable=False)
    
    traitee = db.Column(Boolean, default=False)
    date_traitement = db.Column(DateTime)
    action_prise = db.Column(Text)
    
    def __repr__(self):
        return f'<Alerte {self.type_alerte} - Niveau {self.niveau}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date_alerte': self.date_alerte.isoformat() if self.date_alerte else None,
            'type_alerte': self.type_alerte,
            'niveau': self.niveau,
            'message': self.message,
            'traitee': self.traitee,
            'date_traitement': self.date_traitement.isoformat() if self.date_traitement else None,
            'action_prise': self.action_prise
        }
