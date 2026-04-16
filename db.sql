-- Script de création de la base de données INF5190 Projet Session
-- À placer dans le dossier db/ sous le nom db.sql

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Contravention (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    con_id_poursuite TEXT NOT NULL,
    con_business_id TEXT,
    con_date TEXT,
    con_description TEXT,
    con_adresse TEXT,
    con_date_jugement TEXT,
    con_etablissement TEXT NOT NULL,
    con_montant REAL,
    con_proprietaire TEXT,
    con_ville TEXT,
    con_statut TEXT,
    con_date_statut TEXT,
    con_categorie TEXT,
    est_modifie INTEGER NOT NULL DEFAULT 0,
    est_supprime INTEGER NOT NULL DEFAULT 0,
    etablissement_modif TEXT,
    proprietaire_modif TEXT,
    UNIQUE(con_id_poursuite, con_date, con_etablissement)
);

CREATE INDEX IF NOT EXISTS idx_contravention_etablissement
    ON Contravention(con_etablissement);
CREATE INDEX IF NOT EXISTS idx_contravention_proprietaire
    ON Contravention(con_proprietaire);
CREATE INDEX IF NOT EXISTS idx_contravention_adresse
    ON Contravention(con_adresse);
CREATE INDEX IF NOT EXISTS idx_contravention_date_jugement
    ON Contravention(con_date_jugement);
CREATE INDEX IF NOT EXISTS idx_contravention_supprime
    ON Contravention(est_supprime);

CREATE TABLE IF NOT EXISTS Inspection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    in_nom_etablissement TEXT NOT NULL,
    in_adresse TEXT NOT NULL,
    in_ville TEXT NOT NULL,
    in_date_visite TEXT NOT NULL,
    in_nom_prenom TEXT NOT NULL,
    in_description TEXT NOT NULL,
    date_creation TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ImportLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_import TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Utilisateur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ut_nom_complet TEXT NOT NULL,
    ut_adresse_courriel TEXT NOT NULL UNIQUE,
    ut_liste_etablissements TEXT,
    ut_mots_de_passe TEXT NOT NULL,
    ut_mots_de_passe_salt TEXT NOT NULL,
    ut_photo_profil BLOB,
    date_creation TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_utilisateur_courriel
    ON Utilisateur(ut_adresse_courriel);
