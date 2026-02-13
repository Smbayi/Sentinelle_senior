from flask import Blueprint, render_template, jsonify
from app.models import Patient, Evaluation, Alerte
from app import db

main = Blueprint("main", __name__)

@main.route("/")
def home():
    """Page d'accueil du système"""
    # Statistiques pour le dashboard
    total_patients = Patient.query.filter_by(actif=True).count()
    total_evaluations = Evaluation.query.count()
    alertes_urgentes = Alerte.query.filter_by(traitee=False).count()
    
    return render_template("index.html", 
                         total_patients=total_patients,
                         total_evaluations=total_evaluations,
                         alertes_urgentes=alertes_urgentes)

@main.route("/patients")
def patients():
    """Page de gestion des patients"""
    return render_template("patients.html")

@main.route("/evaluations")
def evaluations():
    """Page de gestion des évaluations"""
    return render_template("evaluations.html")

@main.route("/alertes")
def alertes():
    """Page de gestion des alertes"""
    return render_template("alertes.html")

@main.route("/statistiques")
def statistiques():
    """Page de statistiques et visualisations"""
    return render_template("statistiques.html")

@main.route("/visualisation")
def visualisation():
    """Page de visualisation médicale avec squelette"""
    return render_template("visualisation.html")
