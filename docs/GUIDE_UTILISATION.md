# 🚀 Guide Rapide - API Calendar

## ⚠️ Information importante

**Cette application est une API REST SANS INTERFACE GRAPHIQUE.**  
Il n'y a pas de page web, pas de formulaire, pas de menu de connexion.

Vous devez utiliser:
- **curl** (ligne de commande)
- **Postman** (application graphique)
- **Insomnia** (application graphique)
- Ou tout autre client HTTP

## 📋 Étape 1: Démarrer l'application

```bash
# Arrêter et nettoyer
docker compose down -v

# Démarrer
docker compose up -d

# Attendre 10 secondes que tout démarre
sleep 10

# Créer l'utilisateur ADMIN initial
docker compose exec backend python seed_admin.py
```

Vous obtiendrez un résultat comme:
```
✅ Admin créé avec succès!
   ID: abc123-def456-...
   Email: admin@devops.example.com
   Role: UserRole.ADMIN

💡 Utilisez cet ID dans le header X-User-Id
   Exemple: X-User-Id: abc123-def456-...
```

**NOTEZ CET ID** - vous en aurez besoin pour toutes les requêtes!

## 📋 Étape 2: Tester l'API

### Définir votre ID admin (remplacez par le vôtre!)
```bash
export ADMIN_ID="abc123-def456-..."
```

### 1. Lister les utilisateurs
```bash
curl http://localhost:18000/users/ \
  -H "X-User-Id: $ADMIN_ID"
```

### 2. Créer un utilisateur MODERATOR
```bash
curl -X POST http://localhost:18000/users/ \
  -H "Content-Type: application/json" \
  -H "X-User-Id: $ADMIN_ID" \
  -d '{
    "first_name": "Jean",
    "last_name": "Dupont",
    "email": "jean@example.com",
    "phone_number": "+33601020304",
    "age": 35,
    "job_title": "DevOps Engineer",
    "role": "MODERATOR"
  }'
```

Vous recevrez une réponse JSON avec l'ID du nouvel utilisateur:
```json
{
  "id": "xyz789-...",
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean@example.com",
  ...
}
```

**NOTEZ L'ID** du nouvel utilisateur!

### 3. Créer un événement en tant qu'utilisateur
```bash
# Définir l'ID de Jean
export USER_ID="xyz789-..."

# Créer un événement
curl -X POST http://localhost:18000/events/ \
  -H "Content-Type: application/json" \
  -H "X-User-Id: $USER_ID" \
  -d '{
    "title": "Maintenance serveur",
    "description": "Mise à jour du serveur web",
    "start": "2026-01-20T10:00:00",
    "end": "2026-01-20T12:00:00",
    "color": "#ff5733",
    "resources": ["server-01", "server-02"]
  }'
```

### 4. Lister les événements
```bash
# En tant qu'ADMIN (voit TOUT)
curl http://localhost:18000/events/ \
  -H "X-User-Id: $ADMIN_ID"

# En tant que USER (voit seulement SES événements)
curl http://localhost:18000/events/ \
  -H "X-User-Id: $USER_ID"
```

## 🎯 Utiliser avec Postman (Interface Graphique)

1. **Télécharger Postman**: https://www.postman.com/downloads/

2. **Créer une nouvelle requête**:
   - URL: `http://localhost:18000/users/`
   - Method: GET
   - Headers: Ajouter `X-User-Id` avec la valeur de votre ADMIN_ID

3. **Tester la création d'utilisateur**:
   - URL: `http://localhost:18000/users/`
   - Method: POST
   - Headers: `X-User-Id` et `Content-Type: application/json`
   - Body (raw, JSON):
   ```json
   {
     "first_name": "Marie",
     "last_name": "Martin",
     "email": "marie@example.com",
     "age": 28,
     "role": "USER"
   }
   ```

## 📚 Endpoints disponibles

### Users (ADMIN seulement)
- `POST /users/` - Créer un utilisateur
- `GET /users/` - Lister tous les utilisateurs
- `GET /users/{id}` - Détails d'un utilisateur
- `PUT /users/{id}` - Modifier un utilisateur
- `DELETE /users/{id}` - Supprimer un utilisateur

### Events (Tous les utilisateurs)
- `POST /events/` - Créer un événement
- `GET /events/` - Lister les événements (filtrés selon le rôle)
- `GET /events/{id}` - Détails d'un événement
- `PUT /events/{id}` - Modifier un événement
- `DELETE /events/{id}` - Supprimer un événement

## 🔒 Rôles et Permissions

| Rôle | Peut faire |
|------|------------|
| **ADMIN** | Tout - gérer users, voir/modifier TOUS les événements |
| **MODERATOR** | Voir/modifier événements sauf ceux des ADMIN |
| **USER** | Voir/modifier seulement SES PROPRES événements |

## 🌐 Documentation Interactive

FastAPI génère automatiquement une documentation interactive:

**Swagger UI**: http://localhost:18000/docs  
Vous pouvez tester l'API directement depuis le navigateur!

1. Ouvrez http://localhost:18000/docs
2. Cliquez sur un endpoint
3. Cliquez "Try it out"
4. Ajoutez le header `X-User-Id` dans "Parameters"
5. Remplissez le body si nécessaire
6. Cliquez "Execute"

## ❓ Questions Fréquentes

### Comment me "connecter" ?
Il n'y a pas de connexion traditionnelle. Vous utilisez directement l'ID d'un utilisateur dans le header `X-User-Id`.

### Où est l'interface web ?
Il n'y en a pas. C'est une API pure. Vous pouvez:
- Utiliser curl (ligne de commande)
- Utiliser Postman/Insomnia (applications graphiques)
- Créer votre propre frontend React/Vue/Angular qui appelle cette API

### Comment créer le premier utilisateur ?
Utilisez le script: `docker compose exec backend python seed_admin.py`

### J'ai oublié l'ID admin
Deux solutions:
1. Recréer: `docker compose down -v && docker compose up -d && docker compose exec backend python seed_admin.py`
2. Lire en base: `docker compose exec postgres psql -U devops -d calendar -c "SELECT id, email, role FROM users;"`

## 🛠️ Dépannage

### Les conteneurs ne démarrent pas
```bash
docker compose logs backend
docker compose logs postgres
```

### Table users n'existe pas
```bash
docker compose restart backend
sleep 5
docker compose exec backend python seed_admin.py
```

### Erreur "Invalid user ID"
Vérifiez que l'UUID dans `X-User-Id` existe bien en base.

## 📖 Documentation Complète

Voir le fichier [USER_ACCESS_GUIDE.md](USER_ACCESS_GUIDE.md) pour plus de détails sur les règles d'accès et les exemples avancés.
