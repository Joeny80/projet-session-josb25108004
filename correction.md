# Correction INF5190 Projet de session Hiver 2026

**Étudiant :** Berny Joseph  
**Code permanent :** JSC435667  
**Professeur :** Jacques Berger  
**Total XP implémentés :** 145 XP  
**Minimum requis :** 100 XP

## Note sur le total XP

Le projet implémente 145 XP. Ce total est volontaire et demeure conforme, puisque l'énoncé impose un **minimum** de 100 XP pour un travail individuel.

## Fonctionnalités développées

- A1 — Importation CSV
- A2 — Recherche Flask
- A3 — Synchronisation automatique
- A4 — Service REST par dates
- A5 — Recherche Ajax par période
- A6 — Recherche Ajax par restaurant
- B1 — Courriel automatique
- C1 — Établissements JSON
- C2 — Établissements XML
- C3 — Établissements CSV
- D1 — Demande d’inspection
- D2 — Suppression d’inspection
- D3 — Modification / suppression de contrevenants
- D4 — Basic Auth
- F1 — Déploiement infonuagique

## Structure de remise

- `app.py` : application Flask principale
- `database.py` : couche d’accès aux données
- `config.yaml` : configuration du courriel et de l’authentification
- `requirements.txt` : dépendances Python
- `db/db.sql` : script de création de la base de données
- `db/database.db` : base SQLite vide fournie pour les tests
- `static/style.css` : feuille de style
- `static/a2.js` : JavaScript de la page d’accueil
- `static/d1.js` : JavaScript de la page de plainte
- `templates/a2.html` : page d’accueil
- `templates/d1.html` : page de plainte
- `templates/resultats.html` : page des résultats A2
- `templates/doc.html` : documentation API

## Installation et lancement

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Ouvrir ensuite : `http://127.0.0.1:5000`

## Authentification D4

Identifiants de test pour la correction :

- Username : `admin`
- Password : `secret1234`

Ces identifiants sont fournis uniquement pour les tests du projet académique.

## Comment tester

### A1 — Importation CSV

```bash
python a1.py
```

Télécharge le CSV de Montréal et insère les nouvelles contraventions dans la base.

### A2 — Recherche Flask

1. Lancer `python app.py`
2. Ouvrir `http://127.0.0.1:5000`
3. Saisir un établissement, un propriétaire ou une rue
4. Cliquer sur **Chercher**

### A3 — Synchronisation automatique

Le `BackgroundScheduler` démarre avec l’application et synchronise les données chaque jour à minuit.

### A4 — REST par dates

Exemple :

```bash
curl "http://127.0.0.1:5000/contrevenants?du=2022-05-08&au=2024-05-15"
```

### A5 — Recherche Ajax par période

Sur la page d’accueil, saisir deux dates dans la section **Contraventions par période**, puis cliquer sur **Chercher**.

### A6 — Recherche Ajax par restaurant

Sur la page d’accueil, choisir un restaurant dans la liste déroulante, puis cliquer sur **Afficher les infractions**.

### B1 — Courriel automatique

1. Modifier `config.yaml` au besoin
2. Lancer un SMTP de test
3. Déclencher une importation avec `a1.fetch()` ou `python a1.py`

### C1 — JSON

```bash
curl http://127.0.0.1:5000/api/etablissements
```

### C2 — XML

```bash
curl http://127.0.0.1:5000/api/etablissements.xml
```

### C3 — CSV

```bash
curl http://127.0.0.1:5000/api/etablissements.csv
```

### D1 — Création d’inspection

```bash
curl -X POST http://127.0.0.1:5000/api/inspection \
  -H "Content-Type: application/json" \
  -d '{
    "nom_etablissement": "Restaurant ABC",
    "adresse": "123 rue Principale",
    "ville": "Montréal",
    "date_visite": "2024-06-15",
    "nom_prenom": "Jean Dupont",
    "description": "Présence de moisissures"
  }'
```

### D2 — Suppression d’inspection

```bash
curl -X DELETE "http://127.0.0.1:5000/api/inspection?nom=Restaurant%20ABC&date=2024-06-15"
```

### D3 — Modifier un contrevenant

```bash
curl -X PUT http://127.0.0.1:5000/api/contrevenant/NOM_ORIGINAL \
  -u admin:secret1234 \
  -H "Content-Type: application/json" \
  -d '{
    "nouveau_nom": "Nouveau Nom",
    "nouveau_proprietaire": "Nouveau Propriétaire"
  }'
```

### D3 — Supprimer un contrevenant

```bash
curl -X DELETE http://127.0.0.1:5000/api/contrevenant/NOM_ORIGINAL \
  -u admin:secret1234
```

### D4 — Validation Basic Auth

- Avec les bons identifiants : code 200
- Sans identifiants ou identifiants invalides : code 401

### F1 — Déploiement

URL déployée : `https://inf5190-contraventions.onrender.com`

## Remarques qualité

- Le CSS et le JavaScript des pages ont été déplacés dans des fichiers statiques afin d’éviter de mélanger les langages dans les templates HTML.
- Les routes REST retournent maintenant des codes HTTP plus précis, notamment `404` lorsqu’une ressource à supprimer ou modifier est introuvable.
- La structure de remise respecte l’exigence du dossier `db/` avec `db.sql` et une base vide.
