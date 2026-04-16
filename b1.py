"""
B1 — Envoi automatique par courriel des nouvelles contraventions.

Détecte les nouveaux établissements depuis la dernière importation
et envoie un courriel au destinataire défini dans config.yaml.
"""
import smtplib
from email.mime.text import MIMEText

import yaml


def charger_config():
    """
    Charge la configuration email depuis config.yaml.
    Retourne le sous-dictionnaire 'email'.
    """
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("email", {})


def construire_message(nouveaux, cfg):
    """
    Construit le MIMEText du courriel à partir de la liste
    des nouveaux établissements et de la configuration.
    """
    lignes = "\n".join(f"  • {n}" for n in sorted(nouveaux))
    corps = (
        "Nouveaux établissements en infraction détectés :\n\n"
        + lignes
        + "\n\n— Système de surveillance INF5190"
    )
    sujet = (
        f"[INF5190] {len(nouveaux)}"
        " nouveau(x) contrevenant(s)"
    )
    msg = MIMEText(corps, "plain", "utf-8")
    msg["Subject"] = sujet
    msg["From"] = cfg.get("expediteur", "noreply@inf5190.local")
    msg["To"] = cfg.get("destinataire", "")
    return msg


def _envoyer_via_smtp(msg, cfg):
    """
    Ouvre une connexion SMTP et envoie le message.
    Gère l'authentification si smtp_user est défini.
    """
    with smtplib.SMTP(
        cfg.get("smtp_host", "localhost"),
        int(cfg.get("smtp_port", 1025))
    ) as serveur:
        user = cfg.get("smtp_user", "")
        pwd = cfg.get("smtp_password", "")
        if user and pwd:
            serveur.login(user, pwd)
        serveur.sendmail(
            msg["From"], [msg["To"]], msg.as_string()
        )


def envoyer_courriel(nouveaux):
    """
    Envoie un courriel listant les nouveaux établissements.
    Ne fait rien si la liste est vide ou si le destinataire
    n'est pas configuré dans config.yaml.
    """
    if not nouveaux:
        return
    cfg = charger_config()
    destinataire = cfg.get("destinataire", "")
    if not destinataire:
        print("B1 : aucun destinataire dans config.yaml.")
        return
    msg = construire_message(nouveaux, cfg)
    try:
        _envoyer_via_smtp(msg, cfg)
        print(
            f"B1 : courriel envoyé à {destinataire}"
            f" ({len(nouveaux)} établissements)."
        )
    except Exception as e:
        print(f"B1 : erreur SMTP : {e}")
