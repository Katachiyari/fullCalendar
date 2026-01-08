# Système d'utilisateurs et contrôle d'accès - DevOps Calendar API

## 📋 Vue d'ensemble

Le système implémente 3 rôles utilisateur avec des niveaux d'accès différents:
- **ADMIN**: Accès total à toutes les ressources
- **MODERATOR**: Accès à toutes les ressources sauf celles des ADMIN
- **USER**: Accès uniquement à ses propres ressources

## 🔑 Authentification

L'authentification se fait via le header HTTP `X-User-Id` contenant l'UUID de l'utilisateur.

```bash
# Exemple de requête avec authentification
curl -H "X-User-Id: <uuid-de-l-utilisateur>" http://localhost:18000/events/
```

## 🚀 Démarrage rapide

### 1. Reconstruire et démarrer les conteneurs

```bash
docker-compose down -v  # Supprimer les volumes pour repartir à zéro
docker-compose up --build -d
```

### 2. Créer un utilisateur ADMIN initial

```bash
docker-compose exec backend python seed_admin.py
```

Cette commande affichera l'ID de l'admin créé. Notez cet ID pour l'utiliser dans vos requêtes.

### 3. Tester l'API

```bash
# Récupérer l'ID admin (affiché par seed_admin.py)
ADMIN_ID="<uuid-affiché>"

# Créer un utilisateur MODERATOR
curl -X POST http://localhost:18000/users/ \
  -H "Content-Type: application/json" \
  -H "X-User-Id: $ADMIN_ID" \
  -d '{
    "first_name": "Jean",
    "last_name": "Dupont",
    "email": "jean.dupont@devops.local",
    "phone_number": "+33601020304",
    "age": 35,
    "job_title": "DevOps Engineer",
    "role": "MODERATOR"
  }'

# Créer un utilisateur standard
curl -X POST http://localhost:18000/users/ \
  -H "Content-Type: application/json" \
  -H "X-User-Id: $ADMIN_ID" \
  -d '{
    "first_name": "Marie",
    "last_name": "Martin",
    "email": "marie.martin@devops.local",
    "phone_number": "+33607080910",
    "age": 28,
    "job_title": "Developer",
    "role": "USER"
  }'

# Lister tous les utilisateurs (ADMIN seulement)
curl http://localhost:18000/users/ -H "X-User-Id: $ADMIN_ID"
```

## 📚 API Endpoints

### Users (`/users`)

| Méthode | Endpoint | Accès | Description |
|---------|----------|-------|-------------|
| POST | `/users/` | ADMIN | Créer un utilisateur |
| GET | `/users/` | ADMIN | Lister tous les utilisateurs |
| GET | `/users/{id}` | ADMIN | Récupérer un utilisateur |
| PUT | `/users/{id}` | ADMIN | Mettre à jour un utilisateur |
| DELETE | `/users/{id}` | ADMIN | Supprimer un utilisateur* |

\* Empêche la suppression du dernier ADMIN

### Events (`/events`)

| Méthode | Endpoint | Accès | Description |
|---------|----------|-------|-------------|
| GET | `/events/` | Tous | Liste filtrée selon le rôle** |
| POST | `/events/` | Tous | Créer un événement*** |
| GET | `/events/{id}` | Propriétaire + règles | Récupérer un événement |
| PUT | `/events/{id}` | Propriétaire + règles | Modifier un événement |
| DELETE | `/events/{id}` | Propriétaire + règles | Supprimer un événement |

\*\* Filtrage automatique:
- ADMIN: voit tous les événements
- MODERATOR: voit tous sauf ceux des ADMIN
- USER: voit uniquement ses propres événements

\*\*\* L'`owner_id` est automatiquement défini à l'utilisateur courant

## 🔒 Règles d'autorisation

### check_permission()

Fonction centralisée qui applique les règles suivantes:

| Rôle | Peut accéder à | Ne peut PAS accéder à |
|------|----------------|----------------------|
| ADMIN | Toutes les ressources | Rien |
| MODERATOR | Ressources des USER et MODERATOR | Ressources des ADMIN |
| USER | Ses propres ressources uniquement | Ressources des autres |

### Exemples de contrôle d'accès

```python
# Événement créé par un USER
Event(owner_id="user-123", title="Mon RDV")

# Accès:
# - user-123 (USER): ✅ Peut lire/modifier/supprimer
# - autre-user (USER): ❌ Accès refusé (403)
# - moderator (MODERATOR): ✅ Peut lire/modifier/supprimer
# - admin (ADMIN): ✅ Peut lire/modifier/supprimer
```

```python
# Événement créé par un ADMIN
Event(owner_id="admin-456", title="RDV Admin")

# Accès:
# - admin-456 (ADMIN): ✅ Tous droits
# - autre-admin (ADMIN): ✅ Tous droits
# - moderator (MODERATOR): ❌ Accès refusé (403)
# - user (USER): ❌ Accès refusé (403)
```

## 🗄️ Modèles de données

### User

```python
{
  "id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "age": 18-120,  # optionnel
  "job_title": "string",  # optionnel
  "email": "email@example.com",  # unique
  "phone_number": "string",  # optionnel
  "role": "ADMIN | MODERATOR | USER",
  "created_at": "datetime"
}
```

### Event (modifié)

```python
{
  "id": "uuid",
  "title": "string",
  "description": "string",  # optionnel
  "start": "ISO datetime",
  "end": "ISO datetime",  # optionnel
  "color": "#28a745",
  "resources": ["pod-01", "server-web"],
  "rrule": "FREQ=WEEKLY;BYDAY=MO",  # optionnel
  "all_day": false,
  "owner_id": "uuid",  # ⭐ Nouveau champ
  "created_at": "datetime",
  "deleted_at": "datetime"  # soft delete
}
```

## 🧪 Tests

### Test du contrôle d'accès

```bash
# Créer 3 utilisateurs (admin, moderator, user)
# et noter leurs IDs

# En tant que USER, créer un événement
curl -X POST http://localhost:18000/events/ \
  -H "Content-Type: application/json" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "title": "Maintenance serveur",
    "start": "2026-01-15T10:00:00",
    "end": "2026-01-15T12:00:00",
    "resources": ["server-01"]
  }'

# En tant que MODERATOR, lister les événements
# (devrait voir l'événement du USER mais pas ceux des ADMIN)
curl http://localhost:18000/events/ -H "X-User-Id: $MODERATOR_ID"

# En tant que USER, essayer de modifier l'événement d'un autre
# (devrait retourner 403)
curl -X PUT http://localhost:18000/events/{event-id-autre-user} \
  -H "Content-Type: application/json" \
  -H "X-User-Id: $USER_ID" \
  -d '{"title": "Tentative de modification"}'
```

## 📝 Structure des fichiers

```
app/
├── models/
│   ├── __init__.py
│   └── user.py          # Modèle User + UserRole enum
├── schemas/
│   ├── __init__.py
│   └── user.py          # UserCreate, UserRead, UserUpdate
├── crud/
│   ├── __init__.py
│   └── user.py          # Opérations CRUD pour users
├── routers/
│   ├── events.py        # Routes /events (modifiées)
│   └── users.py         # Routes /users (nouvelles)
├── dependencies.py      # get_current_user, check_permission, require_admin
├── seed_admin.py        # Script pour créer admin initial
├── models.py            # Event model (owner_id ajouté)
├── schemas.py           # Event schemas (owner_id ajouté)
├── crud.py              # Event CRUD (filtrage par rôle)
└── main.py              # App FastAPI (router users ajouté)
```

## ⚠️ Notes de sécurité

### Authentification simple

Ce système utilise un header `X-User-Id` pour l'identification. C'est une approche **simple et déterministe** adaptée au développement et aux environnements contrôlés.

**Pour la production**, il est recommandé d'ajouter:
- JWT tokens avec expiration
- Hashing de mots de passe (bcrypt)
- Rate limiting
- HTTPS obligatoire

La structure actuelle permet d'ajouter facilement une vraie authentification plus tard sans modifier les règles d'autorisation.

## 🔄 Migration depuis l'ancienne version

Si vous avez déjà des événements en base **sans** `owner_id`:

```sql
-- Option 1: Supprimer tous les événements existants
DELETE FROM events;

-- Option 2: Assigner un owner par défaut
UPDATE events SET owner_id = '<uuid-admin>' WHERE owner_id IS NULL;
```

Ou simplement recréer la base:
```bash
docker-compose down -v
docker-compose up --build -d
docker-compose exec backend python seed_admin.py
```

## 🐛 Dépannage

### Erreur "Invalid user ID in X-User-Id header"
- Vérifiez que l'UUID dans le header existe en base
- Utilisez la commande seed_admin.py pour créer un admin
- Listez les users avec un compte admin

### Erreur "Admin access required"
- L'endpoint nécessite un compte ADMIN
- Vérifiez que le role de votre utilisateur est bien "ADMIN"

### Erreur "Email already registered"
- L'email doit être unique
- Utilisez un autre email ou supprimez l'utilisateur existant

### Les événements ne s'affichent pas
- Vérifiez votre rôle: USER ne voit que ses propres événements
- Les événements supprimés (deleted_at non null) ne sont pas listés
- Les MODERATOR ne voient pas les événements des ADMIN
