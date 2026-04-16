"""Couche d'accès aux données — INF5190 Projet de session Hiver 2026."""
import os
import sqlite3

from contravention import Contravention
from inspection import Inspection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "db", "database.db"))


class Database:
    """
    Gère la connexion SQLite et toutes les requêtes de l'application.
    Couvre les tables Contravention, Inspection et Utilisateur.
    """

    def __init__(self):
        """Initialise l'instance sans ouvrir de connexion."""
        self.connection = None

    def obtenir_connexion(self):
        """Retourne la connexion existante ou en crée une nouvelle."""
        if self.connection is None:
            self.connection = sqlite3.connect(DB_PATH)
        return self.connection

    def fermer_connexion(self):
        """Ferme la connexion SQLite et remet l'attribut à None."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    # ---------- Contraventions (A2 / A4 / A6) ----------

    def rechercher(self, terme):
        """
        Recherche les contraventions par établissement, propriétaire
        ou adresse. Exclut les contraventions supprimées (D3).
        Retourne une liste de tuples bruts pour les templates.
        """
        cursor = self.obtenir_connexion().cursor()
        cursor.execute(
            "SELECT * FROM Contravention "
            "WHERE est_supprime = 0 AND ("
            "con_etablissement LIKE ? "
            "OR con_proprietaire LIKE ? "
            "OR con_adresse LIKE ?)",
            (
                "%" + terme + "%",
                "%" + terme + "%",
                "%" + terme + "%",
            )
        )
        return cursor.fetchall()

    def lister_etablissements_distincts(self):
        """
        Retourne la liste distincte de tous les établissements visibles.
        Tient compte des noms modifiés (D3). Utilisé pour A6.
        """
        cursor = self.obtenir_connexion().cursor()
        cursor.execute(
            "SELECT DISTINCT "
            "COALESCE(etablissement_modif, con_etablissement) "
            "FROM Contravention "
            "WHERE est_supprime = 0"
        )
        contraventions = cursor.fetchall()
        return [Contravention.convertir_a6(c[0]) for c in contraventions]

    def filtrer_par_dates(self, du, au):
        """
        Retourne les contraventions entre du et au (ISO 8601).
        Exclut les supprimées. Applique les noms modifiés si présents.
        """
        cursor = self.obtenir_connexion().cursor()
        cursor.execute(
            "SELECT * FROM Contravention "
            "WHERE est_supprime = 0 "
            "AND con_date_jugement BETWEEN ? AND ?",
            (du, au)
        )
        contraventions = cursor.fetchall()
        return [Contravention(*c[:13]) for c in contraventions]

    def filtrer_par_nom(self, nom):
        """
        Retourne toutes les infractions d'un établissement donné.
        Cherche dans le nom modifié s'il est défini.
        """
        cursor = self.obtenir_connexion().cursor()
        cursor.execute(
            "SELECT * FROM Contravention "
            "WHERE est_supprime = 0 "
            "AND COALESCE(etablissement_modif, con_etablissement) LIKE ?",
            ("%" + nom + "%",)
        )
        contraventions = cursor.fetchall()
        return [Contravention(*c[:13]) for c in contraventions]

    def lister_par_infractions(self):
        """
        Retourne les établissements triés par nombre d'infractions
        décroissant. Exclut les supprimés. Utilisé par C1/C2/C3.
        """
        cursor = self.obtenir_connexion().cursor()
        cursor.execute(
            "SELECT "
            "COALESCE(etablissement_modif, con_etablissement), "
            "COUNT(*) "
            "FROM Contravention "
            "WHERE est_supprime = 0 "
            "GROUP BY COALESCE(etablissement_modif, con_etablissement) "
            "HAVING COUNT(*) > 0 "
            "ORDER BY COUNT(*) DESC"
        )
        contraventions = cursor.fetchall()
        return [
            Contravention.convertir_c1(c[0], c[1])
            for c in contraventions
        ]

    # ---------- D3 : modifier / supprimer contrevenants ----------

    def modifier_contrevenant(self, nom_original, nouveau_nom,
                              nouveau_proprietaire):
        """
        Met à jour le nom et le propriétaire d'un contrevenant.
        Retourne True si au moins une ligne a été modifiée.
        """
        connection = self.obtenir_connexion()
        cursor = connection.execute(
            "UPDATE Contravention "
            "SET est_modifie = 1, "
            "etablissement_modif = ?, "
            "proprietaire_modif = ? "
            "WHERE COALESCE(etablissement_modif, con_etablissement) = ? "
            "AND est_supprime = 0",
            (nouveau_nom, nouveau_proprietaire, nom_original)
        )
        connection.commit()
        return cursor.rowcount > 0

    def supprimer_contrevenant(self, nom):
        """
        Marque toutes les contraventions d'un établissement comme
        supprimées. Retourne True si au moins une ligne a été modifiée.
        """
        connection = self.obtenir_connexion()
        cursor = connection.execute(
            "UPDATE Contravention "
            "SET est_supprime = 1 "
            "WHERE COALESCE(etablissement_modif, con_etablissement) = ? "
            "AND est_supprime = 0",
            (nom,)
        )
        connection.commit()
        return cursor.rowcount > 0

    # ---------- Inspections (D1 / D2) ----------

    def lister_inspections(self):
        """Retourne toutes les demandes d'inspection enregistrées."""
        cursor = self.obtenir_connexion().cursor()
        cursor.execute("SELECT * FROM Inspection")
        inspections = cursor.fetchall()
        return [Inspection(*i[1:]) for i in inspections]

    def sauvegarder_inspection(self, inspection):
        """Insère une nouvelle demande d'inspection en base."""
        connection = self.obtenir_connexion()
        connection.execute(
            "INSERT INTO Inspection "
            "(in_nom_etablissement, in_adresse, in_ville, "
            "in_date_visite, in_nom_prenom, in_description) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                inspection.nom_etablissement,
                inspection.adresse,
                inspection.ville,
                inspection.date_visite,
                inspection.nom_prenom,
                inspection.description
            )
        )
        connection.commit()

    def effacer_inspection(self, nom, date):
        """
        Supprime l'inspection correspondant exactement au nom et à la date.
        Retourne True si au moins une ligne a été supprimée.
        """
        connection = self.obtenir_connexion()
        cursor = connection.execute(
            "DELETE FROM Inspection "
            "WHERE in_nom_etablissement = ? "
            "AND in_date_visite = ?",
            (nom, date)
        )
        connection.commit()
        return cursor.rowcount > 0

    # ---------- Utilisateurs ----------

    def creer_utilisateur(self, nom, courriel, liste, mdp, salt):
        """Insère un nouvel utilisateur dans la table Utilisateur."""
        connection = self.obtenir_connexion()
        connection.execute(
            "INSERT INTO Utilisateur "
            "(ut_nom_complet, ut_adresse_courriel, "
            "ut_liste_etablissements, ut_mots_de_passe, "
            "ut_mots_de_passe_salt) "
            "VALUES (?, ?, ?, ?, ?)",
            (nom, courriel, liste, mdp, salt)
        )
        connection.commit()