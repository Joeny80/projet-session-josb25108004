"""
Script d'importation des données de contraventions de la ville de Montréal.

Télécharge le CSV, insère les nouvelles lignes (sans doublons), et retourne
la liste des établissements nouvellement détectés pour B1.
Usage : python a1.py
"""
import csv
import sqlite3
from datetime import datetime

import requests

import os

URL_CSV = (
    "https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0"
    "/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv"
)
DB_PATH = os.environ.get("DB_PATH", "db/database.db")


def telecharger_csv():
    """
    Télécharge le fichier CSV depuis le portail de Montréal.
    Retourne le contenu décodé en UTF-8.
    """
    print("Téléchargement des données...")
    with requests.Session() as session:
        reponse = session.get(URL_CSV, timeout=30)
        reponse.raise_for_status()
        return reponse.content.decode("utf-8-sig", errors="replace")


def inserer_contravention(cursor, row):
    """
    Insère une ligne CSV dans Contravention.
    Utilise INSERT OR IGNORE pour éviter les doublons.
    Retourne True si la ligne a été insérée (nouvelle contravention).
    """
    cursor.execute(
        "INSERT OR IGNORE INTO Contravention"
        "(con_id_poursuite, con_business_id, con_date,"
        " con_description, con_adresse, con_date_jugement,"
        " con_etablissement, con_montant, con_proprietaire,"
        " con_ville, con_statut, con_date_statut, con_categorie)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (row[0], row[1], row[2], row[3], row[4], row[5],
         row[6], row[7], row[8], row[9], row[10], row[11], row[12])
    )
    return cursor.rowcount > 0


def enregistrer_import(connection):
    """
    Insère un enregistrement dans ImportLog avec l'heure actuelle.
    Utilisé par B1 pour détecter les nouvelles contraventions.
    """
    maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connection.execute(
        "INSERT INTO ImportLog (date_import) VALUES (?)",
        (maintenant,)
    )


def importer_donnees(contenu_csv):
    """
    Parcourt le CSV, insère chaque ligne et collecte les nouveaux
    établissements. Retourne un ensemble de noms d'établissements
    nouvellement insérés (sans doublon).
    """
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    lecteur = csv.reader(contenu_csv.splitlines(), delimiter=',')
    next(lecteur, None)

    nouveaux = set()
    compteur = 0
    for row in lecteur:
        if len(row) >= 13:
            if inserer_contravention(cursor, row):
                nouveaux.add(row[6])
                compteur += 1

    enregistrer_import(connection)
    connection.commit()
    connection.close()
    print(f"{compteur} nouvelles contraventions importées.")
    return nouveaux


def fetch():
    """
    Point d'entrée : télécharge, importe et retourne les nouveaux
    établissements détectés. Appelé par le scheduler A3/B1.
    """
    try:
        contenu = telecharger_csv()
        return importer_donnees(contenu)
    except requests.RequestException as e:
        print(f"Erreur téléchargement : {e}")
        return set()
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return set()


if __name__ == "__main__":
    fetch()
