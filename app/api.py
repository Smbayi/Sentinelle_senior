"""
API REST pour le système de suivi de fragilité motrice
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import Patient, Evaluation, MesureMotrice, Alerte
from app.detection import DetecteurFragilite

api_bp = Blueprint('api', __name__)


# ========== ROUTES PATIENTS ==========

@api_bp.route('/patients', methods=['GET'])
def get_patients():
    """Récupérer la liste de tous les patients"""
    patients = Patient.query.filter_by(actif=True).all()
    return jsonify([patient.to_dict() for patient in patients]), 200


@api_bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Récupérer un patient spécifique"""
    patient = Patient.query.get_or_404(patient_id)
    return jsonify(patient.to_dict()), 200


@api_bp.route('/patients', methods=['POST'])
def create_patient():
    """Créer un nouveau patient"""
    data = request.get_json()
    
    try:
        patient = Patient(
            nom=data['nom'],
            prenom=data['prenom'],
            date_naissance=datetime.fromisoformat(data['date_naissance']),
            sexe=data['sexe'],
            telephone=data.get('telephone'),
            adresse=data.get('adresse'),
            notes_medicales=data.get('notes_medicales')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify(patient.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@api_bp.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Mettre à jour un patient"""
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()
    
    try:
        if 'nom' in data:
            patient.nom = data['nom']
        if 'prenom' in data:
            patient.prenom = data['prenom']
        if 'date_naissance' in data:
            patient.date_naissance = datetime.fromisoformat(data['date_naissance'])
        if 'sexe' in data:
            patient.sexe = data['sexe']
        if 'telephone' in data:
            patient.telephone = data['telephone']
        if 'adresse' in data:
            patient.adresse = data['adresse']
        if 'notes_medicales' in data:
            patient.notes_medicales = data['notes_medicales']
        if 'actif' in data:
            patient.actif = data['actif']
        
        db.session.commit()
        return jsonify(patient.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@api_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Désactiver un patient (soft delete)"""
    patient = Patient.query.get_or_404(patient_id)
    patient.actif = False
    db.session.commit()
    return jsonify({'message': 'Patient désactivé'}), 200


# ========== ROUTES ÉVALUATIONS ==========

@api_bp.route('/evaluations', methods=['GET'])
def get_all_evaluations():
    """Récupérer toutes les évaluations"""
    evaluations = Evaluation.query.order_by(Evaluation.date_evaluation.desc()).all()
    return jsonify([eval.to_dict() for eval in evaluations]), 200


@api_bp.route('/patients/<int:patient_id>/evaluations', methods=['GET'])
def get_evaluations(patient_id):
    """Récupérer toutes les évaluations d'un patient"""
    evaluations = Evaluation.query.filter_by(patient_id=patient_id)\
        .order_by(Evaluation.date_evaluation.desc()).all()
    return jsonify([eval.to_dict() for eval in evaluations]), 200


@api_bp.route('/evaluations/<int:evaluation_id>', methods=['GET'])
def get_evaluation(evaluation_id):
    """Récupérer une évaluation spécifique"""
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    return jsonify(evaluation.to_dict()), 200


@api_bp.route('/patients/<int:patient_id>/evaluations', methods=['POST'])
def create_evaluation(patient_id):
    """Créer une nouvelle évaluation"""
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()
    
    try:
        evaluation = Evaluation(
            patient_id=patient_id,
            vitesse_marche=data.get('vitesse_marche'),
            force_prehension=data.get('force_prehension'),
            equilibre_statique=data.get('equilibre_statique'),
            test_leve_chaise=data.get('test_leve_chaise'),
            perte_poids=data.get('perte_poids', False),
            fatigue=data.get('fatigue', False),
            activite_physique_reduite=data.get('activite_physique_reduite', False),
            lenteur_marche=data.get('lenteur_marche', False),
            faiblesse=data.get('faiblesse', False),
            observations=data.get('observations'),
            evaluateur=data.get('evaluateur')
        )
        
        # Calculer le score de fragilité
        DetecteurFragilite.analyser_evaluation(evaluation)
        
        # Générer les recommandations
        DetecteurFragilite.generer_recommandations(evaluation)
        
        db.session.add(evaluation)
        db.session.commit()
        
        # Générer les alertes si nécessaire
        DetecteurFragilite.generer_alertes(patient_id)
        
        return jsonify(evaluation.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ========== ROUTES MESURES ==========

@api_bp.route('/patients/<int:patient_id>/mesures', methods=['GET'])
def get_mesures(patient_id):
    """Récupérer toutes les mesures d'un patient"""
    type_mesure = request.args.get('type')
    query = MesureMotrice.query.filter_by(patient_id=patient_id)
    
    if type_mesure:
        query = query.filter_by(type_mesure=type_mesure)
    
    mesures = query.order_by(MesureMotrice.date_mesure.desc()).all()
    return jsonify([mesure.to_dict() for mesure in mesures]), 200


@api_bp.route('/patients/<int:patient_id>/mesures', methods=['POST'])
def create_mesure(patient_id):
    """Créer une nouvelle mesure motrice"""
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()
    
    try:
        mesure = MesureMotrice(
            patient_id=patient_id,
            type_mesure=data['type_mesure'],
            valeur=data['valeur'],
            unite=data.get('unite', ''),
            source=data.get('source', 'test_manuel'),
            notes=data.get('notes')
        )
        
        db.session.add(mesure)
        db.session.commit()
        
        return jsonify(mesure.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ========== ROUTES ALERTES ==========

@api_bp.route('/patients/<int:patient_id>/alertes', methods=['GET'])
def get_alertes(patient_id):
    """Récupérer toutes les alertes d'un patient"""
    traitees = request.args.get('traitees')
    query = Alerte.query.filter_by(patient_id=patient_id)
    
    if traitees is not None:
        query = query.filter_by(traitee=(traitees.lower() == 'true'))
    
    alertes = query.order_by(Alerte.date_alerte.desc()).all()
    return jsonify([alerte.to_dict() for alerte in alertes]), 200


@api_bp.route('/alertes/<int:alerte_id>', methods=['PUT'])
def traiter_alerte(alerte_id):
    """Marquer une alerte comme traitée"""
    alerte = Alerte.query.get_or_404(alerte_id)
    data = request.get_json()
    
    alerte.traitee = True
    alerte.date_traitement = datetime.utcnow()
    alerte.action_prise = data.get('action_prise', '')
    
    db.session.commit()
    return jsonify(alerte.to_dict()), 200


@api_bp.route('/alertes/non-traitees', methods=['GET'])
def get_alertes_non_traitees():
    """Récupérer toutes les alertes non traitées"""
    alertes = Alerte.query.filter_by(traitee=False)\
        .order_by(Alerte.date_alerte.desc()).all()
    return jsonify([alerte.to_dict() for alerte in alertes]), 200


# ========== ROUTES STATISTIQUES ==========

@api_bp.route('/patients/<int:patient_id>/statistiques', methods=['GET'])
def get_statistiques(patient_id):
    """Récupérer les statistiques d'un patient"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Dernière évaluation
    derniere_eval = Evaluation.query.filter_by(patient_id=patient_id)\
        .order_by(Evaluation.date_evaluation.desc()).first()
    
    # Nombre d'évaluations
    nb_evaluations = Evaluation.query.filter_by(patient_id=patient_id).count()
    
    # Nombre d'alertes non traitées
    nb_alertes = Alerte.query.filter_by(patient_id=patient_id, traitee=False).count()
    
    # Évolution du score de fragilité (dernières 6 évaluations)
    evaluations = Evaluation.query.filter_by(patient_id=patient_id)\
        .order_by(Evaluation.date_evaluation.desc()).limit(6).all()
    
    evolution = [{
        'date': eval.date_evaluation.isoformat(),
        'score': eval.score_fragilite,
        'niveau': eval.niveau_fragilite
    } for eval in reversed(evaluations)]
    
    stats = {
        'patient': patient.to_dict(),
        'derniere_evaluation': derniere_eval.to_dict() if derniere_eval else None,
        'nombre_evaluations': nb_evaluations,
        'alertes_non_traitees': nb_alertes,
        'evolution_fragilite': evolution
    }
    
    return jsonify(stats), 200


@api_bp.route('/statistiques/globales', methods=['GET'])
def get_statistiques_globales():
    """Récupérer les statistiques globales du système"""
    total_patients = Patient.query.filter_by(actif=True).count()
    total_evaluations = Evaluation.query.count()
    total_alertes_non_traitees = Alerte.query.filter_by(traitee=False).count()
    
    # Répartition par niveau de fragilité
    evaluations_recentes = db.session.query(Evaluation)\
        .join(Patient)\
        .filter(Patient.actif == True)\
        .order_by(Evaluation.date_evaluation.desc())\
        .distinct(Evaluation.patient_id)\
        .all()
    
    repartition = {
        'Normal': 0,
        'Pré-fragile': 0,
        'Fragile': 0,
        'Très fragile': 0
    }
    
    for eval in evaluations_recentes:
        if eval.niveau_fragilite in repartition:
            repartition[eval.niveau_fragilite] += 1
    
    stats = {
        'total_patients': total_patients,
        'total_evaluations': total_evaluations,
        'alertes_non_traitees': total_alertes_non_traitees,
        'repartition_fragilite': repartition
    }
    
    return jsonify(stats), 200
