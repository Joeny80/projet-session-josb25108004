"""Modèle de données représentant une contravention alimentaire."""


class Contravention:
    """Représente une contravention issue de la base de données."""

    def __init__(self, con_id_poursuite, con_business_id, con_date,
                 con_description, con_adresse, con_date_jugement,
                 con_etablissement, con_montant, con_proprietaire,
                 con_ville, con_statut, con_date_statut,
                 con_categorie):
        """Initialise une contravention avec tous ses attributs."""
        self.con_id_poursuite = con_id_poursuite
        self.con_business_id = con_business_id
        self.con_date = con_date
        self.con_description = con_description
        self.con_adresse = con_adresse
        self.con_date_jugement = con_date_jugement
        self.con_etablissement = con_etablissement
        self.con_montant = con_montant
        self.con_proprietaire = con_proprietaire
        self.con_ville = con_ville
        self.con_statut = con_statut
        self.con_date_statut = con_date_statut
        self.con_categorie = con_categorie

    def serialiser(self):
        """
        Retourne la contravention sous forme de dictionnaire
        JSON-sérialisable avec toutes les colonnes correctes.
        """
        return {
            "con_id_poursuite":  self.con_id_poursuite,
            "con_business_id":   self.con_business_id,
            "con_date":          self.con_date,
            "con_description":   self.con_description,
            "con_adresse":       self.con_adresse,
            "con_date_jugement": self.con_date_jugement,
            "con_etablissement": self.con_etablissement,
            "con_montant":       self.con_montant,
            "con_proprietaire":  self.con_proprietaire,
            "con_ville":         self.con_ville,
            "con_statut":        self.con_statut,
            "con_date_statut":   self.con_date_statut,
            "con_categorie":     self.con_categorie,
        }

    # Conservé pour compatibilité avec les appels existants
    def as_dict(self):
        """Alias de serialiser() pour compatibilité."""
        return self.serialiser()

    @staticmethod
    def convertir_c1(nom, num):
        """
        Retourne un dict pour C1 (liste établissements/infractions).
        """
        return {
            "con_etablissement": nom,
            "nombre_infraction": num
        }

    @staticmethod
    def convertir_a6(nom):
        """
        Retourne un dict pour A6 (liste déroulante restaurants).
        """
        return {"con_etablissement": nom}
