"""
Module de détection et prévention de la fragilité motrice
Implémente les algorithmes d'analyse et de détection
"""
from datetime import datetime, timedelta
from app.models import Patient, Evaluation, MesureMotrice, Alerte
from app import db


class DetecteurFragilite:
    """Classe pour détecter la fragilité motrice et générer des alertes"""
    
    # Seuils de référence (basés sur la littérature)
    SEUIL_VITESSE_MARCHE_LENTE = 0.8  # m/s (seuil pour la lenteur)
    SEUIL_FORCE_PREHENSION_FAIBLE = {
        'M': 26,  # kg pour hommes
        'F': 16   # kg pour femmes
    }
    SEUIL_EQUILIBRE_FAIBLE = 10  # secondes
    SEUIL_TEST_CHAISE_LENT = 15  # secondes pour 5 répétitions
    
    @staticmethod
    def analyser_evaluation(evaluation):
        """Analyser une évaluation et calculer le score de fragilité"""
        evaluation.calculer_score_fragilite()
        db.session.commit()
        return evaluation
    
    @staticmethod
    def detecter_deterioration(patient_id, jours=30):
        """Détecter une détérioration dans les mesures récentes"""
        date_limite = datetime.utcnow() - timedelta(days=jours)
        
        # Récupérer les évaluations récentes
        evaluations = Evaluation.query.filter(
            Evaluation.patient_id == patient_id,
            Evaluation.date_evaluation >= date_limite
        ).order_by(Evaluation.date_evaluation.desc()).all()
        
        if len(evaluations) < 2:
            return None  # Pas assez de données pour comparer
        
        # Comparer la dernière avec la précédente
        derniere = evaluations[0]
        precedente = evaluations[1]
        
        deteriorations = []
        
        # Vérifier la vitesse de marche
        if derniere.vitesse_marche and precedente.vitesse_marche:
            if derniere.vitesse_marche < precedente.vitesse_marche * 0.9:  # Diminution de 10%
                deteriorations.append({
                    'type': 'vitesse_marche',
                    'valeur_actuelle': derniere.vitesse_marche,
                    'valeur_precedente': precedente.vitesse_marche,
                    'reduction': ((precedente.vitesse_marche - derniere.vitesse_marche) / precedente.vitesse_marche) * 100
                })
        
        # Vérifier la force de préhension
        if derniere.force_prehension and precedente.force_prehension:
            if derniere.force_prehension < precedente.force_prehension * 0.9:
                deteriorations.append({
                    'type': 'force_prehension',
                    'valeur_actuelle': derniere.force_prehension,
                    'valeur_precedente': precedente.force_prehension,
                    'reduction': ((precedente.force_prehension - derniere.force_prehension) / precedente.force_prehension) * 100
                })
        
        # Vérifier le score de fragilité
        if derniere.score_fragilite and precedente.score_fragilite:
            if derniere.score_fragilite > precedente.score_fragilite + 10:  # Augmentation de 10 points
                deteriorations.append({
                    'type': 'score_fragilite',
                    'valeur_actuelle': derniere.score_fragilite,
                    'valeur_precedente': precedente.score_fragilite,
                    'augmentation': derniere.score_fragilite - precedente.score_fragilite
                })
        
        return deteriorations if deteriorations else None
    
    @staticmethod
    def generer_alertes(patient_id):
        """Générer des alertes basées sur l'analyse des données"""
        patient = Patient.query.get(patient_id)
        if not patient:
            return []
        
        alertes_generees = []
        
        # Récupérer la dernière évaluation
        derniere_eval = Evaluation.query.filter_by(patient_id=patient_id)\
            .order_by(Evaluation.date_evaluation.desc()).first()
        
        if not derniere_eval:
            return []
        
        # Vérifier le niveau de fragilité
        if derniere_eval.niveau_fragilite in ['Fragile', 'Très fragile']:
            alerte = Alerte(
                patient_id=patient_id,
                type_alerte='fragilite_accrue',
                niveau='eleve' if derniere_eval.niveau_fragilite == 'Fragile' else 'critique',
                message=f"Patient classé comme {derniere_eval.niveau_fragilite.lower()}. "
                       f"Score de fragilité: {derniere_eval.score_fragilite:.1f}/100. "
                       f"Intervention recommandée."
            )
            alertes_generees.append(alerte)
        
        # Détecter les détériorations
        deteriorations = DetecteurFragilite.detecter_deterioration(patient_id)
        if deteriorations:
            messages = []
            for det in deteriorations:
                if det['type'] == 'vitesse_marche':
                    messages.append(f"Vitesse de marche réduite de {det['reduction']:.1f}%")
                elif det['type'] == 'force_prehension':
                    messages.append(f"Force de préhension réduite de {det['reduction']:.1f}%")
                elif det['type'] == 'score_fragilite':
                    messages.append(f"Score de fragilité augmenté de {det['augmentation']:.1f} points")
            
            niveau = 'moyen' if len(deteriorations) == 1 else 'eleve'
            alerte = Alerte(
                patient_id=patient_id,
                type_alerte='deterioration',
                niveau=niveau,
                message="Détérioration détectée: " + "; ".join(messages)
            )
            alertes_generees.append(alerte)
        
        # Vérifier les seuils critiques
        if derniere_eval.vitesse_marche and derniere_eval.vitesse_marche < DetecteurFragilite.SEUIL_VITESSE_MARCHE_LENTE:
            alerte = Alerte(
                patient_id=patient_id,
                type_alerte='lenteur_marche',
                niveau='moyen',
                message=f"Vitesse de marche très faible ({derniere_eval.vitesse_marche:.2f} m/s). "
                       f"Risque de chute accru."
            )
            alertes_generees.append(alerte)
        
        seuil_force = DetecteurFragilite.SEUIL_FORCE_PREHENSION_FAIBLE.get(patient.sexe)
        if derniere_eval.force_prehension and seuil_force and derniere_eval.force_prehension < seuil_force:
            alerte = Alerte(
                patient_id=patient_id,
                type_alerte='faiblesse',
                niveau='moyen',
                message=f"Force de préhension faible ({derniere_eval.force_prehension:.1f} kg). "
                       f"Exercices de renforcement recommandés."
            )
            alertes_generees.append(alerte)
        
        # Sauvegarder les alertes
        for alerte in alertes_generees:
            # Vérifier si une alerte similaire existe déjà et n'est pas traitée
            existe = Alerte.query.filter_by(
                patient_id=patient_id,
                type_alerte=alerte.type_alerte,
                traitee=False
            ).first()
            
            if not existe:
                db.session.add(alerte)
        
        db.session.commit()
        return alertes_generees
    
    @staticmethod
    def generer_recommandations(evaluation):
        """Générer des recommandations basées sur l'évaluation"""
        recommandations = []
        
        if evaluation.niveau_fragilite == 'Normal':
            recommandations.append("Continuer les activités physiques régulières")
            recommandations.append("Maintenir une alimentation équilibrée")
        elif evaluation.niveau_fragilite == 'Pré-fragile':
            recommandations.append("Programme d'exercices modérés recommandé")
            recommandations.append("Surveillance accrue des indicateurs")
            recommandations.append("Consultation nutritionnelle si nécessaire")
        elif evaluation.niveau_fragilite == 'Fragile':
            recommandations.append("Programme d'exercices supervisé nécessaire")
            recommandations.append("Évaluation médicale approfondie recommandée")
            recommandations.append("Aménagement de l'environnement pour prévenir les chutes")
            recommandations.append("Suivi régulier (mensuel)")
        else:  # Très fragile
            recommandations.append("Intervention médicale urgente recommandée")
            recommandations.append("Programme de rééducation adapté")
            recommandations.append("Aide à domicile ou structure adaptée à considérer")
            recommandations.append("Suivi très régulier (hebdomadaire)")
        
        # Recommandations spécifiques selon les mesures
        if evaluation.vitesse_marche and evaluation.vitesse_marche < 0.8:
            recommandations.append("Exercices de marche et d'équilibre prioritaires")
        
        if evaluation.force_prehension and evaluation.force_prehension < 20:
            recommandations.append("Exercices de renforcement de la préhension")
        
        if evaluation.equilibre_statique and evaluation.equilibre_statique < 10:
            recommandations.append("Travail spécifique sur l'équilibre")
        
        evaluation.recommandations = "\n".join(recommandations)
        db.session.commit()
        
        return recommandations
