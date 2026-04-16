"""
Application Flask principale — INF5190 Projet de session Hiver 2026.

A2 — Recherche de contraventions (établissement, propriétaire, rue)
A3 — Synchronisation quotidienne à minuit (BackgroundScheduler)
A4 — GET /contrevenants?du=&au= (JSON, RAML /doc)
A5 — Recherche par plage de dates (Ajax)
A6 — Recherche par restaurant (Ajax)
B1 — Courriel automatique des nouvelles contraventions (YAML)
C1 — GET /api/etablissements (JSON)
C2 — GET /api/etablissements.xml (XML UTF-8)
C3 — GET /api/etablissements.csv (CSV UTF-8)
D1 — POST /api/inspection + page /plainte (json-schema)
D2 — DELETE /api/inspection
D3 — PUT/DELETE /api/contrevenant/<nom> (Ajax, persistant)
D4 — Basic Auth sur les routes D3
"""
import csv
import io
import os
import re
from functools import wraps

import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from dicttoxml import dicttoxml
from flask import (
    Flask, jsonify, redirect, render_template,
    request, session, url_for
)
from flask import abort as flask_abort
from jsonschema import ValidationError, validate

import a1
import b1
from database import Database
from inspection import Inspection

app = Flask(__name__)


def _env(nom, default=""):
    """Retourne une variable d'environnement nettoyée."""
    val = os.environ.get(nom, default)
    if val is None:
        return default
    return str(val).strip()


def _est_production():
    """Indique si l'application roule en production."""
    return _env("FLASK_ENV", "").lower() == "production"


_secret = _env("SECRET_KEY", "")
if _secret:
    app.config["SECRET_KEY"] = _secret
else:
    if _est_production():
        raise RuntimeError(
            "SECRET_KEY manquante en production. "
            "Définissez la variable d'environnement SECRET_KEY."
        )
    app.config["SECRET_KEY"] = "dev-only-secret-key-change-me"


def charger_config_auth():
    """
    Charge les identifiants Basic Auth depuis config.yaml.
    Retourne un tuple (username, password).
    """
    username = "admin"
    password = ""

    try:
        with open("config.yaml", "r", encoding="utf-8") as fichier:
            cfg = yaml.safe_load(fichier) or {}
            auth = cfg.get("auth", {}) or {}
            username = (auth.get("username") or username).strip()
            password = auth.get("password") or ""
    except Exception:
        pass

    if not username:
        username = "admin"

    return username, str(password)


AUTH_USER, AUTH_PASS = charger_config_auth()


def retourner_401():
    """Retourne une réponse 401 avec l'en-tête WWW-Authenticate."""
    reponse = jsonify({"erreur": "Authentification requise."})
    reponse.status_code = 401
    reponse.headers["WWW-Authenticate"] = 'Basic realm="INF5190 Admin"'
    return reponse


def exiger_basic_auth(fonction):
    """
    Décorateur D4 : protège une route avec HTTP Basic Authentication.
    Retourne 401 si les identifiants sont absents ou incorrects.
    """
    @wraps(fonction)
    def verifier_auth(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return retourner_401()

        if auth.username != AUTH_USER or auth.password != AUTH_PASS:
            return retourner_401()

        return fonction(*args, **kwargs)

    return verifier_auth


SCHEMA_INSPECTION = {
    "type": "object",
    "properties": {
        "nom_etablissement": {"type": "string", "minLength": 1},
        "adresse": {"type": "string", "minLength": 1},
        "ville": {"type": "string", "minLength": 1},
        "date_visite": {
            "type": "string",
            "pattern": r"^\d{4}-\d{2}-\d{2}$",
        },
        "nom_prenom": {"type": "string", "minLength": 1},
        "description": {"type": "string", "minLength": 1},
    },
    "required": [
        "nom_etablissement",
        "adresse",
        "ville",
        "date_visite",
        "nom_prenom",
        "description"
    ],
    "additionalProperties": False,
}

SCHEMA_MODIFICATION = {
    "type": "object",
    "properties": {
        "nouveau_nom": {"type": "string", "minLength": 1},
        "nouveau_proprietaire": {"type": "string", "minLength": 1},
    },
    "required": ["nouveau_nom", "nouveau_proprietaire"],
    "additionalProperties": False,
}


def synchroniser_et_notifier():
    """Importe les données et envoie un courriel s'il y a du nouveau."""
    nouveaux = a1.fetch()
    b1.envoyer_courriel(nouveaux)


def demarrer_scheduler():
    """
    Lance le BackgroundScheduler à minuit.
    En mode debug, évite le double démarrage avec le reloader.
    """
    if app.debug and _env("WERKZEUG_RUN_MAIN", "").lower() != "true":
        return

    scheduler = BackgroundScheduler()
    scheduler.add_job(synchroniser_et_notifier, "cron", hour=0, minute=0)
    scheduler.start()


def valider_date(date_str):
    """Vérifie le format ISO 8601 YYYY-MM-DD."""
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", date_str))


def obtenir_db():
    """Retourne une nouvelle instance connectée de Database."""
    return Database()


def valider_params_dates(du, au):
    """
    Valide les paramètres de dates pour A4.
    Retourne None si OK, ou (dict_erreur, code) si invalide.
    """
    if not du or not au:
        return {"erreur": "Paramètres 'du' et 'au' requis."}, 400

    if not valider_date(du) or not valider_date(au):
        return {"erreur": "Format invalide. Utilisez YYYY-MM-DD."}, 400

    if du > au:
        return {
            "erreur": "'du' doit être antérieure ou égale à 'au'."
        }, 400

    return None


def extraire_donnees_inspection():
    """
    Extrait les données depuis JSON ou formulaire HTML.
    Retourne un dict ou None si aucune donnée exploitable n'est trouvée.
    """
    data_json = request.get_json(silent=True)
    if isinstance(data_json, dict):
        return data_json

    if request.form:
        return {
            "nom_etablissement": request.form.get("in_nom_etablissement", ""),
            "adresse": request.form.get("in_adresse", ""),
            "ville": request.form.get("in_ville", ""),
            "date_visite": request.form.get("in_date_visite", ""),
            "nom_prenom": request.form.get("in_nom_prenom", ""),
            "description": request.form.get("in_description", ""),
        }

    return None


def persister_inspection(data):
    """
    Crée et sauvegarde un objet Inspection depuis un dict validé.
    Retourne l'objet créé.
    """
    inspection = Inspection(
        data["nom_etablissement"],
        data["adresse"],
        data["ville"],
        data["date_visite"],
        data["nom_prenom"],
        data["description"]
    )

    db = obtenir_db()
    db.sauvegarder_inspection(inspection)
    db.fermer_connexion()
    return inspection


@app.route("/", methods=["GET"])
def afficher_accueil():
    """Affiche la page d'accueil avec les formulaires A2, A5 et A6."""
    resultats = session.pop("resultats_recherche", None)
    return render_template("a2.html", resultats=resultats), 200


@app.route("/recherche", methods=["POST"])
def traiter_recherche():
    """
    POST A2 : valide le terme, stocke les résultats en session
    puis redirige vers GET /resultats.
    """
    terme = request.form.get("search", "").strip()

    if not terme:
        flask_abort(400)

    db = obtenir_db()
    contraventions = db.rechercher(terme)
    db.fermer_connexion()

    session["resultats_recherche"] = contraventions
    return redirect(url_for("afficher_resultats"))


@app.route("/resultats", methods=["GET"])
def afficher_resultats():
    """GET A2 — Affiche les résultats de recherche stockés en session."""
    contraventions = session.pop("resultats_recherche", [])
    return render_template("resultats.html", contraventions=contraventions), 200


@app.route("/contrevenants", methods=["GET"])
def lister_contrevenants_par_dates():
    """
    A4 — Retourne les contraventions entre deux dates en JSON.
    Paramètres query : du et au (YYYY-MM-DD).
    """
    du = request.args.get("du", "").strip()
    au = request.args.get("au", "").strip()

    err = valider_params_dates(du, au)
    if err:
        return jsonify(err[0]), err[1]

    db = obtenir_db()
    contraventions = db.filtrer_par_dates(du, au)
    db.fermer_connexion()

    return jsonify([c.as_dict() for c in contraventions]), 200


@app.route("/api/restaurants", methods=["GET"])
def lister_restaurants():
    """Retourne la liste distincte de tous les établissements visibles."""
    db = obtenir_db()
    etablissements = db.lister_etablissements_distincts()
    db.fermer_connexion()
    return jsonify(etablissements), 200


@app.route("/api/contraventions", methods=["GET"])
def lister_contraventions_par_restaurant():
    """
    A6 — Retourne toutes les infractions d'un restaurant.
    Paramètre query : restaurant.
    """
    nom = request.args.get("restaurant", "").strip()

    if not nom:
        return jsonify({"erreur": "Paramètre 'restaurant' requis."}), 400

    db = obtenir_db()
    contraventions = db.filtrer_par_nom(nom)
    db.fermer_connexion()

    return jsonify([c.as_dict() for c in contraventions]), 200


@app.route("/api/etablissements", methods=["GET"])
def lister_etablissements_json():
    """C1 — Liste triée par infractions décroissantes, JSON."""
    db = obtenir_db()
    liste = db.lister_par_infractions()
    db.fermer_connexion()
    return jsonify(liste), 200


@app.route("/api/etablissements.xml", methods=["GET"])
def lister_etablissements_xml():
    """C2 — Mêmes données que C1, format XML UTF-8."""
    db = obtenir_db()
    liste = db.lister_par_infractions()
    db.fermer_connexion()

    xml_bytes = dicttoxml(
        liste,
        custom_root="etablissements",
        attr_type=False
    )

    return app.response_class(
        xml_bytes,
        status=200,
        mimetype="application/xml; charset=utf-8"
    )


@app.route("/api/etablissements.csv", methods=["GET"])
def lister_etablissements_csv():
    """C3 — Mêmes données que C1, format CSV UTF-8."""
    db = obtenir_db()
    liste = db.lister_par_infractions()
    db.fermer_connexion()

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["con_etablissement", "nombre_infraction"]
    )
    writer.writeheader()
    writer.writerows(liste)

    return app.response_class(
        output.getvalue(),
        status=200,
        mimetype="text/csv; charset=utf-8"
    )


@app.route("/plainte", methods=["GET"])
def afficher_plainte():
    """Affiche le formulaire de plainte D1."""
    return render_template("d1.html"), 200


@app.route("/api/inspection", methods=["POST"])
def creer_inspection():
    """
    D1 — Crée une demande d'inspection.
    Accepte JSON ou formulaire. Valide avec json-schema.
    """
    data = extraire_donnees_inspection()

    if data is None:
        return jsonify({"erreur": "Corps JSON invalide."}), 400

    try:
        validate(instance=data, schema=SCHEMA_INSPECTION)
    except ValidationError as e:
        return jsonify({"erreur": e.message}), 400

    inspection = persister_inspection(data)

    if request.get_json(silent=True) is not None:
        return jsonify(inspection.as_dict()), 201

    return redirect(url_for("afficher_accueil"))


@app.route("/api/inspection", methods=["DELETE"])
def supprimer_inspection():
    """
    D2 — Supprime une inspection par nom et date.
    Retourne 404 si aucune inspection ne correspond.
    """
    nom = request.args.get("nom", "").strip()
    date = request.args.get("date", "").strip()

    if not nom or not date:
        return jsonify({"erreur": "Paramètres 'nom' et 'date' requis."}), 400

    if not valider_date(date):
        return jsonify({"erreur": "Format de date invalide. YYYY-MM-DD."}), 400

    db = obtenir_db()
    db.effacer_inspection(nom, date)
    db.fermer_connexion()

    return jsonify({
        "nom": nom,
        "date": date,
        "message": "Inspection supprimée."
    }), 200


@app.route("/api/contrevenant/<string:nom>", methods=["PUT"])
@exiger_basic_auth
def modifier_contrevenant(nom):
    """
    D3 — Modifie le nom et le propriétaire d'un contrevenant.
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"erreur": "Corps JSON invalide."}), 400

    try:
        validate(instance=data, schema=SCHEMA_MODIFICATION)
    except ValidationError as e:
        return jsonify({"erreur": e.message}), 400

    db = obtenir_db()
    db.modifier_contrevenant(
        nom,
        data["nouveau_nom"],
        data["nouveau_proprietaire"]
    )
    db.fermer_connexion()

    return jsonify({
        "nom_original": nom,
        "nouveau_nom": data["nouveau_nom"],
        "nouveau_proprietaire": data["nouveau_proprietaire"],
        "message": "Contrevenant modifié."
    }), 200


@app.route("/api/contrevenant/<string:nom>", methods=["DELETE"])
@exiger_basic_auth
def supprimer_contrevenant(nom):
    """
    D3 — Suppression logique d'un contrevenant.
    """
    db = obtenir_db()
    db.supprimer_contrevenant(nom)
    db.fermer_connexion()

    return jsonify({
        "nom": nom,
        "message": "Contrevenant supprimé."
    }), 200


@app.route("/doc", methods=["GET"])
def afficher_documentation():
    """Affiche la documentation HTML générée depuis le RAML."""
    return render_template("doc.html"), 200


@app.errorhandler(400)
def gerer_400(err):
    """Gestionnaire 400 — Requête invalide."""
    return jsonify({"erreur": "Requête invalide.", "code": 400}), 400


@app.errorhandler(401)
def gerer_401(err):
    """Gestionnaire 401 — Non autorisé."""
    return jsonify({
        "erreur": "Authentification requise.",
        "code": 401
    }), 401


@app.errorhandler(404)
def gerer_404(err):
    """Gestionnaire 404 — Ressource introuvable."""
    return jsonify({"erreur": "Introuvable.", "code": 404}), 404


@app.errorhandler(405)
def gerer_405(err):
    """Gestionnaire 405 — Méthode non autorisée."""
    return jsonify({
        "erreur": "Méthode non autorisée.",
        "code": 405
    }), 405


@app.errorhandler(500)
def gerer_500(err):
    """Gestionnaire 500 — Erreur interne du serveur."""
    return jsonify({"erreur": "Erreur interne.", "code": 500}), 500


if __name__ == "__main__":
    debug = not _est_production()
    app.debug = debug

    demarrer_scheduler()

    port = int(_env("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=debug)