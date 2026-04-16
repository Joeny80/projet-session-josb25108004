# Correction INF5190 Projet de session Hiver 2026

**Étudiant :** Berny Joseph  
**Code permanent :** JOSB25108004  
**Professeur :** Jacques Berger  
**Total XP implémentés :** 145 XP  
**Minimum requis :** 100 XP

---

## Note sur le total XP

Le projet implémente 145 XP. Ce total est volontaire et demeure conforme, puisque l'énoncé impose un **minimum** de 100 XP pour un travail individuel.

---

## Application déployée (F1)

**URL : https://joeny.pythonanywhere.com**

La base de données est déjà peuplée. Toutes les fonctionnalités sont testables directement en ligne sans installation.

---

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
- D1 — Demande d'inspection
- D2 — Suppression d'inspection
- D3 — Modification / suppression de contrevenants
- D4 — Basic Auth
- F1 — Déploiement infonuagique

---

## Structure de remise

- `app.py` : application Flask principale
- `database.py` : couche d'accès aux données
- `config.yaml` : configuration du courriel et de l'authentification
- `requirements.txt` : dépendances Python
- `db/db.sql` : script de création de la base de données
- `db/database.db` : base SQLite vide fournie pour les tests
- `static/style.css` : feuille de style
- `static/a2.js` : JavaScript de la page d'accueil
- `static/d1.js` : JavaScript de la page de plainte
- `templates/a2.html` : page d'accueil
- `templates/d1.html` : page de plainte
- `templates/resultats.html` : page des résultats A2
- `templates/doc.html` : documentation API

---

## Installation locale

```bash
git clone https://github.com/Joeny80/projet-session-josb25108004.git
cd projet-session-josb25108004
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\Activate.ps1       # Windows PowerShell
pip install -r requirements.txt
$env:SECRET_KEY="dev-key"       # Windows PowerShell
export SECRET_KEY="dev-key"     # Linux/macOS
python app.py
```

Puis importer les données au premier lancement :

```bash
python a1.py
```

Ouvrir ensuite : http://127.0.0.1:5000

---

## Authentification D4

- Username : `admin`
- Password : `secret1234`

---

## Comment tester — En ligne (PythonAnywhere)

### A1 — Importation CSV

Script `a1.py` exécuté automatiquement via le scheduler (A3). Pour tester localement :

```bash
python a1.py
```

### A2 — Recherche Flask

1. Ouvrir https://joeny.pythonanywhere.com
2. Saisir un établissement, un propriétaire ou une rue
3. Cliquer sur **Chercher**
4. Les résultats s'affichent sur une nouvelle page avec toutes les données de chaque contravention

### A3 — Synchronisation automatique

Le `BackgroundScheduler` démarre avec l'application et synchronise les données chaque jour à minuit automatiquement.

### A4 — REST par dates

```bash
curl "https://joeny.pythonanywhere.com/contrevenants?du=2022-05-08&au=2024-05-15"
```

### A5 — Recherche Ajax par période

1. Ouvrir https://joeny.pythonanywhere.com
2. Saisir deux dates dans la section **Contraventions par période**
3. Cliquer sur **Chercher**
4. Un tableau s'affiche avec le nom de l'établissement et le nombre de contraventions

### A6 — Recherche Ajax par restaurant

1. Ouvrir https://joeny.pythonanywhere.com
2. Choisir un restaurant dans la liste déroulante
3. Cliquer sur **Afficher les infractions**
4. Les infractions du restaurant s'affichent via Ajax

### B1 — Courriel automatique

1. Modifier `config.yaml` avec l'adresse destinataire
2. Lancer un serveur SMTP de test : `python -m smtpd -n -c DebuggingServer localhost:1025`
3. Exécuter `python a1.py` — un courriel listant les nouvelles contraventions est envoyé

### C1 — JSON

```bash
curl https://joeny.pythonanywhere.com/api/etablissements
```

### C2 — XML

```bash
curl https://joeny.pythonanywhere.com/api/etablissements.xml
```

### C3 — CSV

```bash
curl https://joeny.pythonanywhere.com/api/etablissements.csv
```

### D1 — Création d'inspection (interface web)

1. Ouvrir https://joeny.pythonanywhere.com/plainte
2. Remplir le formulaire et soumettre

**Ou via curl :**

```bash
curl -X POST https://joeny.pythonanywhere.com/api/inspection \
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

Réponse attendue : code `201`

### D2 — Suppression d'inspection

```bash
curl -X DELETE "https://joeny.pythonanywhere.com/api/inspection?nom=Restaurant%20ABC&date=2024-06-15"
```

Réponse attendue : code `200`

### D3 — Modifier un contrevenant

```bash
curl -X PUT https://joeny.pythonanywhere.com/api/contrevenant/NOM_ORIGINAL \
  -u admin:secret1234 \
  -H "Content-Type: application/json" \
  -d '{
    "nouveau_nom": "Nouveau Nom",
    "nouveau_proprietaire": "Nouveau Propriétaire"
  }'
```

Réponse attendue : code `200`

### D3 — Supprimer un contrevenant

```bash
curl -X DELETE https://joeny.pythonanywhere.com/api/contrevenant/NOM_ORIGINAL \
  -u admin:secret1234
```

Réponse attendue : code `200`

### D3 — Via l'interface Ajax

1. Ouvrir https://joeny.pythonanywhere.com
2. Faire une recherche par période (A5)
3. Dans les résultats, utiliser les boutons **Modifier** ou **Supprimer** sur un contrevenant

### D4 — Validation Basic Auth

```bash
# Avec les bons identifiants → code 200
curl -u admin:secret1234 -X DELETE \
  https://joeny.pythonanywhere.com/api/contrevenant/NOM_ORIGINAL

# Sans identifiants → code 401
curl -X DELETE \
  https://joeny.pythonanywhere.com/api/contrevenant/NOM_ORIGINAL
```

### F1 — Déploiement

URL déployée : `https://joeny.pythonanywhere.com`

---

## Remarques qualité

- Le CSS et le JavaScript sont dans des fichiers statiques séparés (pas de mélange dans les templates HTML).
- Les routes REST retournent des codes HTTP précis : `201` (création), `200` (succès), `404` (ressource introuvable), `401` (non authentifié), `400` (données invalides).
- La structure respecte l'exigence du dossier `db/` avec `db.sql` et une base vide.
- `pycodestyle` ne soulève aucune erreur sur l'ensemble des fichiers `.py`.
