# 📅 Calendrier avec Gestion Utilisateurs et Rôles

> Un système complet de calendrier et de gestion d'événements avec authentification JWT, gestion des rôles et interface web moderne.

## 🎯 Objectif

Créer une application de calendrier full-stack avec:
- ✅ Authentification JWT sécurisée
- ✅ Gestion des rôles (ADMIN, MODERATOR, USER)
- ✅ Contrôle d'accès par rôle
- ✅ Interface moderne avec Bulma CSS
- ✅ Calendrier interactif avec FullCalendar
- ✅ Gestion complète des profils utilisateur
- ✅ Panel d'administration

---

## 🚀 Démarrage Rapide

### Prérequis
- Docker & Docker Compose
- Python 3.11+
- Un navigateur moderne

### Installation & Lancement

```bash
# Cloner le projet
cd /media/james/DATA1/python/fullCalendar

# Lancer avec Docker Compose
docker-compose up -d

# Attendre que les conteneurs soient prêts (≈ 30 secondes)
sleep 30

# Accéder à l'application
open http://localhost:8000/login
# ou naviguer manuellement vers http://localhost:8000/login
```

### Credentials de Test
| Rôle | Email | Mot de passe |
|------|-------|--------------|
| ADMIN | admin@devops.example.com | Admin@123456 |

> **Note**: Ces identifiants par défaut sont créés automatiquement lors du démarrage

---

## 📖 Flux d'Utilisation

### 1️⃣ Inscription Nouvelle Utilisateur
```
http://localhost:8000/register
→ Remplir le formulaire d'inscription
→ Confirmation automatique vers la page de login
```

### 2️⃣ Connexion
```
http://localhost:8000/login
→ Entrer email et mot de passe
→ Redirection automatique vers l'application
```

### 3️⃣ Utilisation du Calendrier
```
http://localhost:8000/calendar
→ Voir les événements
→ Créer de nouveaux événements
→ Modifier/supprimer ses événements
→ Accéder au profil ou admin (selon le rôle)
```

### 4️⃣ Gestion du Profil
```
http://localhost:8000/profile
→ Modifier les infos personnelles
→ Changer le mot de passe
→ Supprimer le compte
```

### 5️⃣ Admin - Gestion des Utilisateurs (ADMIN only)
```
http://localhost:8000/admin/users
→ Voir tous les utilisateurs
→ Modifier les rôles
→ Désactiver/supprimer des comptes
```

---

## 🏗️ Architecture Technique

### Backend - FastAPI
```
Endpoints Principaux:

Authentification:
  POST   /auth/register              Créer un compte
  POST   /auth/login                 Se connecter
  GET    /auth/me                    Infos utilisateur
  PUT    /auth/me                    Mettre à jour profil
  POST   /auth/change-password       Changer mot de passe
  DELETE /auth/me                    Supprimer compte
  POST   /auth/logout                Déconnexion

Événements:
  GET    /events/                    Lister les événements
  POST   /events/                    Créer un événement
  GET    /events/{id}                Détails d'un événement
  PUT    /events/{id}                Modifier un événement
  DELETE /events/{id}                Supprimer un événement

Utilisateurs (ADMIN only):
  GET    /users/                     Lister tous les utilisateurs
  GET    /users/{id}                 Détails d'un utilisateur
  PUT    /users/{id}                 Modifier un utilisateur
  DELETE /users/{id}                 Supprimer un utilisateur
```

### Frontend - Bulma + SPA
```
Pages:
  /login                             Connexion
  /register                          Inscription
  /calendar                          Calendrier principal
  /profile                           Profil utilisateur
  /admin/users                       Gestion des utilisateurs (ADMIN)

Modules JS:
  static/js/auth.js                  Gestion de l'authentification
  static/js/navbar.js                Composant navbar
```

---

## 🔐 Système de Sécurité

### Authentification JWT
- Tokens générés avec `PyJWT`
- Stockés dans `localStorage`
- Envoyés via header `Authorization: Bearer <token>`
- Expiration: 24 heures

### Mots de Passe
- Hachés avec `bcrypt`
- Sel automatique
- Minimum 8 caractères
- Vérification sécurisée

### Contrôle d'Accès
```
ADMIN:
  ✓ Voir tous les utilisateurs
  ✓ Modifier tous les rôles
  ✓ Voir tous les événements
  ✓ Supprimer des utilisateurs

MODERATOR:
  ✓ Voir ses événements
  ✓ Voir les événements de son groupe
  ✓ Créer/modifier ses événements

USER:
  ✓ Voir ses propres événements
  ✓ Créer/modifier ses événements
```

---

## 📊 Modèles de Données

### Utilisateur (User)
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "Jean",
  "last_name": "Dupont",
  "phone_number": "0612345678",
  "job_title": "Developer",
  "age": 30,
  "hashed_password": "$2b$12$...",
  "is_active": true,
  "role": "USER",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Événement (Event)
```json
{
  "id": "uuid",
  "title": "Réunion d'équipe",
  "description": "Réunion hebdomadaire",
  "date_time": "2025-01-20T14:00:00Z",
  "user_id": "uuid",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

---

## 🛠️ Configuration

### Fichier `.env` (Optionnel)
```env
# Base de données
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/fullcalendar

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=["http://localhost:8000"]
```

### Docker Compose
```yaml
# Voir docker-compose.yml
Services:
  - app:  FastAPI application (port 8000)
  - db:   PostgreSQL database (port 5432)
```

---

## 📝 Utilisation de l'API

### Exemple: Créer un Événement

#### JavaScript
```javascript
const token = localStorage.getItem('token');

const event = {
    title: "Ma réunion",
    description: "Description",
    date_time: "2025-01-20T14:00:00Z"
};

const response = await fetch('/events/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(event)
});

const created = await response.json();
console.log('Événement créé:', created.id);
```

#### cURL
```bash
curl -X POST http://localhost:8000/events/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ma réunion",
    "description": "Description",
    "date_time": "2025-01-20T14:00:00Z"
  }'
```

---

## 🧪 Tests

### Script de Test Automatisé
```bash
python test_api.py
```

Cela teste:
- ✓ Inscription
- ✓ Connexion
- ✓ Profil utilisateur
- ✓ Changement de mot de passe
- ✓ Créer/modifier/supprimer des événements

### Swagger UI
```
http://localhost:8000/docs
```

Accédez à l'interface Swagger pour tester les endpoints directement.

---

## 📦 Dépendances

### Backend (Python)
```
FastAPI==0.115.2
SQLAlchemy==2.0.35
asyncpg==0.30.0
PyJWT==2.8.1
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
Pydantic==2.5.2
```

### Frontend (CDN)
```
Bulma@0.9.4
Font Awesome@6.4.0
FullCalendar@6.1.10
```

---

## 🐛 Dépannage

### Le navigateur affiche une erreur 401
**Cause**: Token expiré ou invalide
```javascript
// Solution: Se reconnecter
window.location.href = '/login';
```

### L'API retourne une erreur CORS
**Cause**: Configuration CORS manquante
```python
# Vérifier dans app/main.py que CORSMiddleware est configuré
```

### La base de données ne se connecte pas
**Cause**: Container PostgreSQL non démarré
```bash
# Solution
docker-compose restart db
```

### Oublié le mot de passe de l'admin
**Solution**: Réinitialiser avec seed
```bash
docker-compose down
docker volume rm fullcalendar_pg_data
docker-compose up
```

---

## 📈 Fonctionnalités Futures (Roadmap)

- [ ] Confirmation d'email
- [ ] Réinitialisation de mot de passe par email
- [ ] Partage d'événements
- [ ] Notifications en temps réel (WebSocket)
- [ ] Récurrences d'événements
- [ ] Export calendrier (iCal/Google Calendar)
- [ ] Intégration Slack
- [ ] Mode sombre
- [ ] Application mobile
- [ ] Tests automatisés complets

---

## 📚 Documentation Complète

Pour une documentation détaillée et technique:
```bash
cat DOCUMENTATION.md
```

---

## 🤝 Support

### Logs
```bash
# Voir les logs de l'application
docker-compose logs app

# Voir les logs de la base de données
docker-compose logs db

# Voir tous les logs
docker-compose logs
```

### Réinitialiser l'Application
```bash
# Arrêter et supprimer tous les conteneurs
docker-compose down

# Supprimer les volumes (data)
docker volume rm fullcalendar_pg_data

# Redémarrer
docker-compose up
```

---

## 📄 Licence

Ce projet est fourni à titre d'exemple éducatif.

---

## 📧 Informations de Contact

Pour toute question ou suggestion, consultez la documentation ou les logs.

---

**Version**: 1.0.0  
**Statut**: ✅ Production Ready  
**Dernière mise à jour**: Janvier 2025

```
🎉 Merci d'utiliser ce calendrier!
```
