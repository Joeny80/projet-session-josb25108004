"""Modèle de données représentant une demande d'inspection."""


class Inspection:
    """Représente une demande d'inspection soumise par un citoyen."""

    def __init__(self, nom_etablissement, adresse, ville,
                 date_visite, nom_prenom, description):
        """Initialise une inspection avec tous ses attributs."""
        self.nom_etablissement = nom_etablissement
        self.adresse = adresse
        self.ville = ville
        self.date_visite = date_visite
        self.nom_prenom = nom_prenom
        self.description = description

    def serialiser(self):
        """
        Retourne l'inspection sous forme de dictionnaire
        JSON-sérialisable.
        """
        return {
            "nom_etablissement": self.nom_etablissement,
            "adresse":           self.adresse,
            "ville":             self.ville,
            "date_visite":       self.date_visite,
            "nom_prenom":        self.nom_prenom,
            "description":       self.description,
        }

    def as_dict(self):
        """Alias de serialiser() pour compatibilité."""
        return self.serialiser()
