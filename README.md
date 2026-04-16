# INF5190 - Projet de Session

**Contraventions Alimentaires - Ville de Montréal**  
Hiver 2026

---

## Description

Application web Flask permettant de consulter et gérer les contraventions alimentaires émises par la ville de Montréal. Le projet offre des fonctionnalités de recherche, de signalement et d'administration via une API REST documentée.

**Total XP implémentés:** 145 XP (minimum requis: 100 XP)

---

## Installation (obligatoire — environnement virtuel)

Le projet DOIT être exécuté dans un environnement virtuel Python.

```bash
# 1) Créer l'environnement virtuel
python3 -m venv venv

# 2) Activer
# Linux/macOS
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1

# 3) Installer les dépendances
pip install -r requirements.txt

# 4) Initialiser la base de données (si nécessaire)
sqlite3 db/database.db < db/db.sql

# 5) Lancer
export SECRET_KEY="dev-key"      # macOS/Linux
set SECRET_KEY=dev-key           # Windows (cmd)
$env:SECRET_KEY="dev-key"        # Windows (PowerShell)

python app.py
```

## Installation Rapide

### 1. Cloner et naviguer dans le projet

```bash
cd projet
```

### 2. Créer l'environnement virtuel

```bash
python3 -m venv venv
```

### 3. Activer l'environnement

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5. Lancer l'application

```bash
python app.py
```

### 6. Ouvrir dans le navigateur

http://127.0.0.1:5000

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
- **F1:** Déploiement sur Render.com configuré

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
├── runtime.txt           # Version Python
├── Procfile              # Commande de démarrage
├── render.yaml           # Configuration Render
├── db/
│   ├── db.sql            # Script de création de la base
│   └── database.db       # Base de données SQLite
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

## API REST

### Documentation complète

Accéder à: http://127.0.0.1:5000/doc

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

## Tests

### Tester l'importation (A1)

```bash
python a1.py
```

### Tester l'API (A4)

```bash
curl "http://127.0.0.1:5000/contrevenants?du=2022-01-01&au=2024-12-31"
```

### Tester la création d'inspection (D1)

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

### Tester la modification (D3/D4)

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

## Déploiement (F1)

Application déployée sur Render :  
```
https://TON-APP.onrender.com
```

## Déploiement (F1)

### Sur Render.com

1. Créer un compte sur https://render.com
2. Créer un dépôt Git privé et pousser le code
3. Sur Render: "New Web Service" → connecter le dépôt
4. Configuration:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1`
5. Déployer

---

## Auteur

**Berny Joseph**  
Code permanent: JSC435667  
Cours: INF5190 - Programmation web avancée  
Session: Hiver 2026

---

## Licence

Projet académique - Université du Québec à Montréal
