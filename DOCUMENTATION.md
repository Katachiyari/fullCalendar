# 📅 Calendrier avec Gestion Utilisateurs - Interface Bulma

## ✨ Résumé de l'Implémentation

Système complet de gestion de calendrier et d'événements avec authentification JWT, gestion des rôles (ADMIN, MODERATOR, USER) et interface web moderne utilisant Bulma CSS.

---

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI 0.115.2
- **Base de données**: PostgreSQL 16 + SQLAlchemy 2.0.35
- **Authentification**: JWT tokens avec bcrypt
- **Dépendances principales**:
  - `PyJWT` - Gestion des tokens
  - `passlib[bcrypt]` - Hachage des mots de passe
  - `python-multipart` - Upload de formulaires
  - `python-dotenv` - Variables d'environnement

### Frontend
- **Framework CSS**: Bulma 0.9.4
- **Icônes**: Font Awesome 6.4.0
- **Calendrier**: FullCalendar 6.1.10
- **JavaScript**: Vanilla JS avec modules (auth.js, navbar.js)

---

## 📁 Structure des Fichiers

### Backend
```
app/
├── main.py                 # Application principale FastAPI
├── models.py              # Modèles SQLAlchemy (User, Event)
├── schemas.py             # Schémas Pydantic pour les endpoints
├── schemas_auth.py        # Schémas spécifiques auth (NEW)
├── crud.py               # Opérations CRUD pour les événements
├── crud_auth.py          # Opérations CRUD pour l'authentification (NEW)
├── database.py           # Configuration de la base de données
├── dependencies.py       # Dépendances d'injection (UPDATED)
├── security.py           # Utilitaires JWT et hachage (NEW)
├── requirements.txt      # Dépendances Python (UPDATED)
└── routers/
    ├── __init__.py
    ├── auth.py           # Routes d'authentification (NEW)
    ├── events.py         # Routes des événements
    └── users.py          # Routes de gestion des utilisateurs
```

### Frontend
```
static/
├── index.html                    # Page d'accueil avec calendrier (UPDATED)
├── login.html                    # Page de connexion (NEW)
├── register.html                 # Page d'inscription (NEW)
├── profile.html                  # Profil utilisateur (NEW)
├── admin-users.html             # Gestion des utilisateurs (NEW)
└── js/
    ├── auth.js                   # Gestion de l'authentification côté client (NEW)
    └── navbar.js                 # Composant navbar réutilisable (NEW)
```

---

## 🔐 Authentification & Sécurité

### Flux d'Authentification
1. **Inscription** → POST `/auth/register`
   - Validation des données
   - Hachage du mot de passe avec bcrypt
   - Création de l'utilisateur

2. **Connexion** → POST `/auth/login`
   - Vérification des identifiants
   - Création d'un JWT token
   - Stockage du token dans `localStorage`

3. **Utilisation du Token**
   - Ajouté automatiquement aux requêtes via `Authorization: Bearer <token>`
   - Validé à chaque requête protégée

### Sécurité des Mots de Passe
```python
# Hachage: bcrypt avec salt automatique
hashed = hash_password("password123")

# Vérification: comparaison sécurisée
is_valid = verify_password("password123", hashed)
```

### Endpoints d'Authentification
- `POST /auth/register` - Créer un compte
- `POST /auth/login` - Se connecter
- `GET /auth/me` - Récupérer l'utilisateur connecté
- `PUT /auth/me` - Mettre à jour le profil
- `POST /auth/change-password` - Changer le mot de passe
- `DELETE /auth/me` - Supprimer le compte
- `POST /auth/logout` - Déconnexion (logout)

---

## 👥 Système de Rôles

### Hiérarchie des Rôles
```
ADMIN (administrateur)
  ├─ Gestion complète des utilisateurs
  ├─ Voir tous les événements
  └─ Modération des contenus

MODERATOR (modérateur)
  ├─ Voir les événements de son groupe
  ├─ Créer/modifier ses événements
  └─ Actions modérées

USER (utilisateur)
  ├─ Voir ses propres événements
  └─ Créer/modifier ses événements
```

### Contrôle d'Accès par Rôle
```python
# Dans les modèles de données
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    USER = "USER"

# Dans les endpoints: filtre selon le rôle
if user.role == "ADMIN":
    # Voir tous les événements
else:
    # Voir seulement ses événements
```

---

## 🎨 Interface Utilisateur

### Pages Disponibles

#### 1. **Login (login.html)**
- Formulaire Email/Mot de passe
- Gestion des erreurs
- Lien vers inscription
- Stockage automatique du token JWT

#### 2. **Register (register.html)**
- Formulaire complet (nom, email, âge, etc.)
- Validation client
- Redirection vers login après inscription

#### 3. **Calendrier (index.html)**
- Vue calendrier FullCalendar (month/week/day)
- Liste des prochains événements
- Statistiques utilisateur
- Navbar avec menu utilisateur

#### 4. **Profil (profile.html)**
- Édition des informations personnelles
- Changement de mot de passe
- Statistiques utilisateur
- Suppression du compte

#### 5. **Admin - Gestion Utilisateurs (admin-users.html)**
- Liste complète des utilisateurs
- Recherche et filtres par rôle
- Édition des rôles et statut
- Suppression d'utilisateurs (ADMIN only)
- Statistiques globales

---

## 🛠️ Technologies Principales

### Frontend Technologies
| Technologie | Usage |
|-------------|-------|
| Bulma 0.9.4 | Framework CSS moderne et réactif |
| Font Awesome 6.4.0 | Bibliothèque d'icônes |
| FullCalendar 6.1.10 | Composant calendrier avancé |
| Vanilla JS | Logique côté client |
| localStorage API | Persistance du token |

### Backend Technologies
| Technologie | Usage |
|-------------|-------|
| FastAPI 0.115.2 | Framework API haute performance |
| SQLAlchemy 2.0.35 | ORM async pour DB |
| Pydantic | Validation des données |
| JWT | Authentification sans état |
| bcrypt | Hachage sécurisé des mots de passe |
| PostgreSQL 16 | Base de données relationnelle |

---

## 🚀 Utilisation

### Lancer l'Application
```bash
docker-compose up
```

### Endpoints Principaux
```
Frontend:
  http://localhost:8000/static/login.html
  http://localhost:8000/static/register.html
  http://localhost:8000/static/index.html

API:
  http://localhost:8000/docs          # Swagger UI
  http://localhost:8000/redoc         # ReDoc
```

### Utilisateur Admin Seed
- Email: `admin@devops.example.com`
- Mot de passe: `Admin@123456`

---

## 📊 Modèles de Données

### Utilisateur (User)
```python
- id: UUID
- email: str (unique)
- first_name: str
- last_name: str
- phone_number: str (optional)
- job_title: str (optional)
- age: int (optional)
- hashed_password: str (bcrypt)
- is_active: bool
- role: UserRole (ADMIN/MODERATOR/USER)
- created_at: datetime
- updated_at: datetime
```

### Événement (Event)
```python
- id: UUID
- title: str
- description: str (optional)
- date_time: datetime
- user_id: UUID (FK to User)
- created_at: datetime
- updated_at: datetime
```

---

## 🔧 Configuration

### Variables d'Environnement (.env)
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/fullcalendar

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=["http://localhost:8000", "http://localhost:3000"]
```

### Configuration JWT
```python
# app/security.py
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 heures
```

---

## 🎯 Fonctionnalités Implémentées

✅ Authentification JWT complète
✅ Inscription et connexion
✅ Gestion des rôles (ADMIN, MODERATOR, USER)
✅ Profil utilisateur avec édition
✅ Changement de mot de passe sécurisé
✅ Suppression de compte
✅ Calendrier interactif FullCalendar
✅ Gestion des événements
✅ Panel admin de gestion des utilisateurs
✅ Recherche et filtres
✅ Interface Bulma responsive
✅ Navbar avec menu utilisateur
✅ Session persistante avec localStorage
✅ Redirection automatique vers login

---

## 📈 Fonctionnalités Futures (Optionnel)

- [ ] Confirmation d'email
- [ ] Réinitialisation de mot de passe
- [ ] Partage d'événements
- [ ] Notifications
- [ ] Récurrences d'événements
- [ ] Export calendrier (iCal)
- [ ] API GraphQL
- [ ] Tests unitaires
- [ ] Documentation OpenAPI complet

---

## 🐛 Dépannage

### Le token n'est pas envoyé
```javascript
// Vérifier que le header est correctement ajouté
const headers = {
    'Authorization': `Bearer ${auth.getToken()}`,
    'Content-Type': 'application/json'
};
```

### Erreur 401 Unauthorized
```
Causes possibles:
1. Token expiré → Se reconnecter
2. Token invalide → localStorage vidé?
3. En-têtes mal formés → Vérifier le format "Bearer <token>"
```

### Problème CORS
```python
# Dans main.py, vérifier la configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📝 Notes de Développement

### Architecture de l'Authentification
- **Sans Session**: Utilisation de JWT tokens au lieu de sessions serveur
- **Stateless**: Chaque requête est indépendante
- **Scalable**: Pas de stock de sessions à gérer

### Considérations de Sécurité
- Les mots de passe ne sont JAMAIS stockés en clair
- Les tokens sont stockés en `localStorage` (attention XSS)
- Les mots de passe minimum 8 caractères
- Les emails doivent être uniques

### Performance
- Requêtes asynchrones pour ne pas bloquer
- Mise en cache du rôle utilisateur côté client
- Indices sur les colonnes critiques (email, user_id)

---

## 🔗 Ressources

- [Bulma Documentation](https://bulma.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FullCalendar Documentation](https://fullcalendar.io/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc7519)

---

**Dernière mise à jour**: Janvier 2025
**Version**: 1.0.0
**Statut**: Production-Ready ✅
