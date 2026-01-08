# 🔧 DÉPANNAGE - LE LOGIN NE FONCTIONNE PAS

## ⚠️ PROBLÈME DIAGNOSTIQUÉ

Le seed_admin.py n'était **pas à jour** avec le système JWT. Il ne créait pas de mot de passe hashé correctement.

---

## ✅ SOLUTION - 3 ÉTAPES

### ÉTAPE 1: Mettre à jour le seed
Le fichier `app/seed_admin.py` a été corrigé pour créer un utilisateur avec mot de passe hashé.

### ÉTAPE 2: Initialiser la base de données

```bash
# Option A: Si vous avez Python localement
python init_db.py

# Option B: Avec Docker
docker-compose down -v
docker-compose up
# Attendez que le message "Uvicorn running on" apparaisse
```

### ÉTAPE 3: Tester l'authentification

```bash
# Tester le système
python test_auth_system.py
```

---

## 🚀 DÉMARRAGE COMPLET (Sans Docker)

Si vous n'avez pas Docker, suivez ceci:

### 1. Installer les dépendances
```bash
pip install -r app/requirements.txt
```

### 2. Configurer PostgreSQL (optionnel)
```bash
# Si vous n'avez pas PostgreSQL, créer une DB SQLite temporaire
# Éditer app/database.py:
# DATABASE_URL = "sqlite:///./test.db"
```

### 3. Initialiser la DB et créer admin
```bash
python init_db.py
```

Output attendu:
```
📝 Initialisation de la base de données...
✅ Tables créées avec succès

👤 Création de l'utilisateur admin...
✅ Admin créé avec succès!
   Email: admin@devops.example.com
   Password: Admin@123456
   Role: ADMIN

✨ Initialisation terminée!
```

### 4. Démarrer l'API
```bash
python -m uvicorn app.main:app --reload
```

Output attendu:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 5. Ouvrir dans le navigateur
```
http://localhost:8000/static/login.html
```

### 6. Se connecter
```
Email:    admin@devops.example.com
Password: Admin@123456
```

---

## 🔍 DIAGNOSTIQUER LE PROBLÈME

### Test 1: Vérifier le système d'auth
```bash
python test_auth_system.py
```

Doit afficher:
```
✅ Test des mots de passe réussi!
✨ Test JWT réussi!
✅ TOUS LES TESTS RÉUSSIS!
```

### Test 2: Vérifier la base de données
```bash
# Si PostgreSQL est en local
psql -U postgres -d fullcalendar -c "SELECT email, role FROM users;"

# Doit montrer:
#        email             | role
# --------------------------------
# admin@devops.example.com | ADMIN
```

### Test 3: Tester manuellement l'API
```bash
# Enregistrement d'un nouvel utilisateur
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "password": "TestPass123"
  }'

# Connexion
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@devops.example.com",
    "password": "Admin@123456"
  }'

# Doit retourner un token JWT
```

---

## 🐛 PROBLÈMES COURANTS

### ❌ "Unauthorized (401)" au login
**Cause**: Mot de passe incorrect ou admin non créé
**Solution**:
```bash
# Réinitialiser
python init_db.py
# Ou si Docker:
docker-compose down -v
docker-compose up
```

### ❌ "Cannot find module 'app'"
**Cause**: Python path mal configuré
**Solution**:
```bash
# Faire depuis le répertoire racine
cd /media/james/DATA1/python/fullCalendar
python init_db.py
```

### ❌ "Database connection refused"
**Cause**: PostgreSQL n'est pas en cours d'exécution
**Solution**:
```bash
# Option A: Avec Docker
docker-compose up -d db

# Option B: Utiliser SQLite (dev uniquement)
# Éditer app/database.py et changer DATABASE_URL
```

### ❌ "Table users does not exist"
**Cause**: Les tables n'ont pas été créées
**Solution**:
```bash
python init_db.py
```

---

## 🔐 TESTER CHAQUE ENDPOINT

### 1. Enregistrer un nouvel utilisateur
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jean",
    "last_name": "Dupont",
    "email": "jean@example.com",
    "age": 30,
    "phone_number": "0612345678",
    "job_title": "Developer",
    "password": "MyPassword123"
  }'

# Response: {"email": "jean@example.com", "role": "USER", ...}
```

### 2. Se connecter
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jean@example.com",
    "password": "MyPassword123"
  }' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo $TOKEN
```

### 3. Accéder à son profil
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Response: {"email": "jean@example.com", "first_name": "Jean", ...}
```

### 4. Modifier son profil
```bash
curl -X PUT http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jean-Pierre"
  }'
```

### 5. Changer le mot de passe
```bash
curl -X POST http://localhost:8000/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "MyPassword123",
    "new_password": "NewPassword456"
  }'
```

---

## ✨ VÉRIFICATION FINALE

Quand tout fonctionne:

✅ Login avec admin@devops.example.com / Admin@123456  
✅ Créer un nouveau compte  
✅ Se connecter avec le nouveau compte  
✅ Voir le calendrier  
✅ Créer des événements  

---

## 📚 FICHIERS IMPORTANTS

| Fichier | Rôle |
|---------|------|
| `app/security.py` | Hash & JWT |
| `app/schemas_auth.py` | Validation |
| `app/crud_auth.py` | BD operations |
| `app/routers/auth.py` | Endpoints |
| `app/seed_admin.py` | Créer admin (MISE À JOUR) |
| `init_db.py` | Initialisation (NOUVEAU) |
| `test_auth_system.py` | Tests (NOUVEAU) |

---

## 🎯 RÉSUMÉ DES CHANGEMENTS

| Fichier | Changement |
|---------|-----------|
| seed_admin.py | ✅ Ajout du mot de passe hashé |
| init_db.py | ✨ Nouveau - Initialisation rapide |
| test_auth_system.py | ✨ Nouveau - Tests d'authentification |

---

## 🚨 SI RIEN NE FONCTIONNE

### Option nucléaire: Réinitialisation complète
```bash
# 1. Arrêter tout
docker-compose down -v

# 2. Nettoyer la BD
rm -f test.db  # Si vous utilisez SQLite

# 3. Repartir de zéro
python init_db.py
python -m uvicorn app.main:app --reload

# 4. Tester
python test_api.py
```

### Vérifier les logs
```bash
# Terminal 1: Voir les erreurs de l'API
python -m uvicorn app.main:app --reload

# Terminal 2: Tester
python test_auth_system.py
curl -X POST http://localhost:8000/auth/login ...
```

---

## ✅ CHECKLIST DE DÉBOGAGE

- [ ] Python 3.9+ installé
- [ ] `python -m pip install -r app/requirements.txt` exécuté
- [ ] `python init_db.py` exécuté avec succès
- [ ] `python test_auth_system.py` passe tous les tests
- [ ] `python -m uvicorn app.main:app --reload` fonctionne
- [ ] http://localhost:8000/docs affiche Swagger
- [ ] http://localhost:8000/static/login.html charge la page
- [ ] Login avec admin@devops.example.com / Admin@123456 fonctionne

---

**Créé**: Janvier 2026
**Dernière mise à jour**: Après correction du seed_admin.py
