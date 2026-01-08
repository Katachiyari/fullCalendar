# 🔑 TESTER LE LOGIN IMMÉDIATEMENT

## ⚡ Démarrage en 3 minutes

### 1. Installer les dépendances
```bash
cd /media/james/DATA1/python/fullCalendar
pip install -r app/requirements.txt
```

**Doit montrer**: "Successfully installed..."

### 2. Initialiser la DB et créer l'admin
```bash
python init_db.py
```

**Doit montrer**:
```
✅ Tables créées avec succès
✅ Admin créé avec succès!
   Email: admin@devops.example.com
   Password: Admin@123456
```

### 3. Lancer l'API
```bash
python -m uvicorn app.main:app --reload
```

**Doit montrer**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

⏸️ **NE PAS FERMER CE TERMINAL** - Laisser tourner

### 4. Tester dans un AUTRE terminal

#### Test 1: API Swagger
```bash
# Ouvrir dans le navigateur
open http://localhost:8000/docs
```

#### Test 2: Login avec cURL
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@devops.example.com",
    "password": "Admin@123456"
  }'
```

**Doit retourner**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "email": "admin@devops.example.com",
    "first_name": "Admin",
    "role": "ADMIN"
  }
}
```

✅ **Si vous voyez le token, le login fonctionne!**

#### Test 3: Page Web
```bash
# Ouvrir dans le navigateur
open http://localhost:8000/login
```

Puis entrer:
- Email: `admin@devops.example.com`
- Mot de passe: `Admin@123456`

---

## 🆘 SI ÇA NE FONCTIONNE PAS

### ❌ "ModuleNotFoundError"
```bash
# Vous n'êtes pas dans le bon répertoire
cd /media/james/DATA1/python/fullCalendar
python init_db.py
```

### ❌ "No module named 'aiosqlite'"
```bash
# Les dépendances ne sont pas installées
pip install -r app/requirements.txt
```

### ❌ "InvalidRequestException" à init_db.py
```bash
# Il y a un problème de DB existante
rm -f calendar.db
python init_db.py
```

### ❌ "Connection refused" en testant
```bash
# L'API n'est pas lancée
# Vérifier Terminal 1: python -m uvicorn app.main:app --reload
```

---

## ✨ SI TOUT FONCTIONNE

Vous pouvez maintenant:

✅ **Login avec admin**:
- Email: `admin@devops.example.com`
- Password: `Admin@123456`

✅ **Créer un nouveau compte** en cliquant "S'inscrire"

✅ **Voir le calendrier** après connexion

✅ **Aller au profil** pour éditer infos

✅ **Admin panel** (visible si ADMIN)

---

## 📚 FICHIERS IMPORTANTS

```
/media/james/DATA1/python/fullCalendar/
├── app/
│   ├── main.py              ← API principale
│   ├── security.py          ← JWT & password
│   ├── crud_auth.py         ← DB operations
│   ├── routers/auth.py      ← Endpoints auth
│   └── seed_admin.py        ← Créer admin (MIS À JOUR)
├── init_db.py               ← Initialiser DB (NOUVEAU)
├── test_auth_system.py      ← Tests (NOUVEAU)
├── frontend/                ← SPA React + Bulma (UI)
│   └── src/                 ← Code frontend
└── calendar.db              ← DB SQLite (créée après init_db.py)
```

---

## 🧪 TESTS INCLUS

### Test 1: Authentification
```bash
python test_auth_system.py
```

### Test 2: API complète
```bash
python test_api.py
```

### Test 3: Swagger UI
```
http://localhost:8000/docs
```

---

## 🎯 RÉSUMÉ

| Étape | Commande | Résultat |
|-------|----------|----------|
| 1 | `pip install -r app/requirements.txt` | Dépendances OK |
| 2 | `python init_db.py` | Admin créé |
| 3 | `python -m uvicorn app.main:app --reload` | API lancée |
| 4 | Ouvrir `http://localhost:8000/login` | Page affichée |
| 5 | Login avec admin@devops.example.com / Admin@123456 | ✅ OK |

**Total**: ~3 minutes

---

## 💡 NOTES

- **Pas besoin de Docker** - Utilise SQLite en local
- **Base de données**: `calendar.db` (crée automatiquement)
- **Port**: `8000` (défaut FastAPI)
- **Email test**: Créer via "S'inscrire"
- **Mot de passe**:min 8 caractères

---

**Créé**: Janvier 2026
**Status**: ✅ Testé et fonctionnel
