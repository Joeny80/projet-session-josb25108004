# INF5190 - Projet de Session

**Contraventions Alimentaires - Ville de Montréal**  
Hiver 2026

---

## Description

Application web Flask permettant de consulter et gérer les contraventions alimentaires émises par la ville de Montréal. Le projet offre des fonctionnalités de recherche, de signalement et d'administration via une API REST documentée.

**Total XP implémentés:** 145 XP (minimum requis: 100 XP)

---

## Auteur

**Berny Joseph**  
Code permanent: JOSB25108004  
Cours: INF5190 - Programmation web avancée  
Session: Hiver 2026

---

## Déploiement (F1) — Application en ligne

L'application est déployée et accessible directement sans installation :

**URL : https://joeny.pythonanywhere.com**

- Page d'accueil : https://joeny.pythonanywhere.com
- Documentation API : https://joeny.pythonanywhere.com/doc
- La base de données est déjà peuplée avec les données de la ville de Montréal

---

## Installation locale (environnement virtuel obligatoire)

### 1. Cloner le dépôt

```bash
git clone https://github.com/Joeny80/projet-session-josb25108004.git
cd projet-session-josb25108004
```

### 2. Créer et activer l'environnement virtuel

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Initialiser la base de données

Un fichier `db/database.db` vide est fourni. Pour le recréer si nécessaire :

```bash
sqlite3 db/database.db < db/db.sql
```

### 5. Définir la clé secrète

**Linux/macOS:**
```bash
export SECRET_KEY="dev-key"
```

**Windows (PowerShell):**
```powershell
$env:SECRET_KEY="dev-key"
```

**Windows (cmd):**
```bash
set SECRET_KEY=dev-key
```

### 6. Lancer l'application

```bash
python app.py
```

### 7. Ouvrir dans le navigateur

http://127.0.0.1:5000

### 8. Importer les données (obligatoire au premier lancement)

```bash
python a1.py
```

Télécharge le CSV de la ville de Montréal et peuple la base de données.

---

## Fonctionnalités

### A - Fonctionnalités de base
- **A1:** Importation CSV automatique depuis la ville de Montréal
- **A2:** Recherche par établissement, propriétaire ou rue
- **A3:** Synchronisation quotidienne à minuit (BackgroundScheduler)
- **A4:** API REST `/contrevenants?du=&au=` (JSON)
- **A5:** Recherche Ajax par plage de dates
- **A6:** Recherche Ajax par restaurant (liste déroulante)

### B - Notifications
- **B1:** Courriel automatique des nouvelles contraventions (configurable dans `config.yaml`)

### C - Services REST multiples
- **C1:** `/api/etablissements` (JSON)
- **C2:** `/api/etablissements.xml` (XML UTF-8)
- **C3:** `/api/etablissements.csv` (CSV UTF-8)

### D - Inspections et modifications
- **D1:** Formulaire de plainte + API REST POST `/api/inspection`
- **D2:** Suppression d'inspection DELETE `/api/inspection`
- **D3:** Modification/suppression de contrevenants via Ajax
- **D4:** Authentification Basic Auth sur les routes D3

### F - Déploiement
- **F1:** Déploiement sur PythonAnywhere

---

## Structure du Projet

```
projet/
├── a1.py                 # Script d'importation CSV (A1)
├── app.py                # Application Flask principale
├── b1.py                 # Envoi de courriels (B1)
├── config.yaml           # Configuration email et auth
├── contravention.py      # Modèle de données Contravention
├── database.py           # Couche d'accès aux données
├── inspection.py         # Modèle de données Inspection
├── correction.md         # Guide de correction détaillé
├── requirements.txt      # Dépendances Python
├── db/
│   ├── db.sql            # Script de création de la base
│   └── database.db       # Base de données SQLite vide
└── templates/
    ├── a2.html           # Page d'accueil
    ├── d1.html           # Formulaire de plainte
    ├── doc.html          # Documentation API
    └── resultats.html    # Page de résultats
```

---

## Configuration

### Email (B1)

Éditer `config.yaml`:

```yaml
email:
  destinataire: votre@email.com
  expediteur: noreply@inf5190.local
  smtp_host: localhost
  smtp_port: 1025
```

### Authentification (D4)

Éditer `config.yaml`:

```yaml
auth:
  username: admin
  password: secret1234
```

**Identifiants par défaut:**
- Username: `admin`
- Password: `secret1234`

---

## API REST — Documentation complète

- **Local :** http://127.0.0.1:5000/doc
- **En ligne :** https://joeny.pythonanywhere.com/doc

### Endpoints principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/contrevenants` | GET | Liste des contraventions par dates |
| `/api/etablissements` | GET | Liste JSON des établissements |
| `/api/etablissements.xml` | GET | Liste XML des établissements |
| `/api/etablissements.csv` | GET | Liste CSV des établissements |
| `/api/inspection` | POST | Créer une demande d'inspection |
| `/api/inspection` | DELETE | Supprimer une inspection |
| `/api/contrevenant/<nom>` | PUT | Modifier un contrevenant (Auth) |
| `/api/contrevenant/<nom>` | DELETE | Supprimer un contrevenant (Auth) |

---

## Tests en ligne — PythonAnywhere

### A4 — REST par dates

```bash
curl "https://joeny.pythonanywhere.com/contrevenants?du=2022-01-01&au=2024-12-31"
```

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

### D1 — Création d'inspection

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

### D2 — Suppression d'inspection

```bash
curl -X DELETE "https://joeny.pythonanywhere.com/api/inspection?nom=Restaurant%20ABC&date=2024-06-15"
```

### D3 — Modifier un contrevenant (Basic Auth requis)

```bash
curl -X PUT https://joeny.pythonanywhere.com/api/contrevenant/NOM_ORIGINAL \
  -u admin:secret1234 \
  -H "Content-Type: application/json" \
  -d '{
    "nouveau_nom": "Nouveau Nom",
    "nouveau_proprietaire": "Nouveau Propriétaire"
  }'
```

### D3 — Supprimer un contrevenant (Basic Auth requis)

```bash
curl -X DELETE https://joeny.pythonanywhere.com/api/contrevenant/NOM_ORIGINAL \
  -u admin:secret1234
```

### D4 — Validation Basic Auth

```bash
# Avec les bons identifiants → code 200
curl -u admin:secret1234 https://joeny.pythonanywhere.com/api/contrevenant/NOM_ORIGINAL

# Sans identifiants → code 401
curl https://joeny.pythonanywhere.com/api/contrevenant/NOM_ORIGINAL
```

---

## Tests locaux

### A1 — Importation CSV

```bash
python a1.py
```

### A4 — REST par dates

```bash
curl "http://127.0.0.1:5000/contrevenants?du=2022-01-01&au=2024-12-31"
```

### D1 — Création d'inspection

```bash
curl -X POST http://127.0.0.1:5000/api/inspection \
  -H "Content-Type: application/json" \
  -d '{
    "nom_etablissement": "Test Restaurant",
    "adresse": "123 Test Street",
    "ville": "Montréal",
    "date_visite": "2024-06-15",
    "nom_prenom": "Jean Test",
    "description": "Problème d'hygiène observé"
  }'
```

### D3/D4 — Modifier avec authentification

```bash
curl -X PUT http://127.0.0.1:5000/api/contrevenant/NOM \
  -u admin:secret1234 \
  -H "Content-Type: application/json" \
  -d '{"nouveau_nom":"Nouveau","nouveau_proprietaire":"Prop"}'
```

---

## Vérification PEP8

```bash
python -m pycodestyle --max-line-length=79 *.py
```

**Résultat attendu:** Aucune erreur

---

## Licence

Projet académique - Université du Québec à Montréal
