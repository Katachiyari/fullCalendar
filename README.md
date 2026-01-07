# DevOps Calendar 📅

Un calendrier événementiel moderne et sécurisé pour les équipes DevOps, construit avec **FastAPI**, **PostgreSQL**, **FullCalendar** et **Bootstrap 5.3**.

## ✨ Caractéristiques

### 🎯 Fonctionnalités Principales
- **Calendrier interactif** : Affichage par mois/semaine/jour avec FullCalendar v6
- **Création d'événements** : Modal Bootstrap avec validation frontend/backend
- **Édition & Suppression** : Drag-drop pour déplacer les événements
- **Récurrence** : Support des règles RRULE (FREQ=WEEKLY, BYDAY, etc.)
- **Ressources** : Associer des événements à des Kubernetes pods ou serveurs
- **Descriptions** : Champ texte pour détails, runbooks, liens

### 🔒 Sécurité & Validation
- **Dates antérieures interdites** : Aucun événement ne peut être créé dans le passé
- **Délai minimum** : Les événements doivent être créés au minimum **15 minutes à l'avance**
- **Édition bloquée** : Les événements passés ne peuvent pas être modifiés ou supprimés
- **Validation triple couche** :
  - Frontend: Attribut `min` HTML5 + vérification JavaScript
  - Backend: Pydantic validators + HTTPException 403
  - UX: Toasts Bootstrap pour feedback utilisateur

### 🛠️ Stack Technique

| Component | Version | Rôle |
|-----------|---------|------|
| **FastAPI** | 0.115.2 | Framework API asynchrone |
| **SQLAlchemy** | 2.0.35 | ORM avec support async |
| **AsyncPG** | 0.29.0 | Driver PostgreSQL asynchrone |
| **PostgreSQL** | 16-alpine | Base de données |
| **Pydantic** | 2.9.2 | Validation des données |
| **FullCalendar** | 6.1.17 | Calendrier interactif |
| **Bootstrap** | 5.3.2 | UI responsive |
| **Uvicorn** | 0.32.0 | Serveur ASGI |

## 🚀 Démarrage Rapide

### Prérequis
- Docker & Docker Compose
- Port 8000 disponible (API)
- Port 5432 disponible (PostgreSQL, optionnel)

### Installation & Lancement

```bash
# Cloner et naviguer
git clone <repo-url>
cd devops-calendar

# Démarrer les services
docker compose up -d

# Vérifier le statut
docker compose ps
```

L'application sera disponible à:
- **Frontend** : http://localhost:8000/static/index.html
- **API** : http://localhost:8000/events
- **Documentation API** : http://localhost:8000/docs

### Arrêt
```bash
docker compose down
```

## 📖 Utilisation

### Créer un Événement

1. **Bouton "Nouvel évènement"** ou **cliquer sur une date** dans le calendrier
2. Remplir le modal :
   - **Titre** : Libellé de l'événement
   - **Début/Fin** : Dates et heures (minimum +15 min)
   - **Couleur** : Code hex ou sélecteur
   - **Ressources** : Cocher les pods/serveurs affectés
   - **Récurrence** : RRULE optionnelle (ex: `FREQ=WEEKLY;BYDAY=MO,WE`)
   - **Journée entière** : Cocher si pas d'heure spécifique
   - **Description** : Notes additionnelles

3. **Enregistrer** → L'événement apparaît dans le calendrier

### Éditer / Supprimer

- **Éditer** : Drag-drop vers une nouvelle date
- **Supprimer** : Cliquer sur l'événement → Confirmer

⚠️ Les événements passés sont **verrouillés** (non modifiables)

## 🔌 API REST

### Endpoints

#### GET /events/
Récupérer tous les événements

```bash
curl http://localhost:8000/events/
```

Réponse (200 OK):
```json
[
  {
    "id": "3e9aa9c9-...",
    "title": "Déploiement prod",
    "start": "2026-02-10T15:00:00",
    "end": "2026-02-10T16:00:00",
    "color": "#28a745",
    "resources": ["pod-01", "server-db"],
    "rrule": "FREQ=WEEKLY;BYDAY=FR",
    "all_day": false,
    "description": "Lancer la release 2.0",
    "created_at": "2026-01-07T14:30:00.123456"
  }
]
```

#### POST /events/
Créer un événement

```bash
curl -X POST http://localhost:8000/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Maintenance DB",
    "start": "2026-02-15T22:00:00",
    "end": "2026-02-16T00:00:00",
    "color": "#ffc107",
    "resources": ["server-db"],
    "description": "Migration v13 → v14"
  }'
```

**Validations** :
- `start` : Obligatoire, doit être >= maintenant + 15 minutes
- `title` : Obligatoire, max 255 caractères
- `color` : Format hex (#RRGGBB)

**Réponses** :
- `201 Created` : Événement créé
- `422 Unprocessable Entity` : Validation échouée (date passée, format invalide, etc.)

#### PUT /events/{event_id}
Modifier un événement

```bash
curl -X PUT http://localhost:8000/events/3e9aa9c9-... \
  -H "Content-Type: application/json" \
  -d '{"start": "2026-02-15T20:00:00"}'
```

**Réponses** :
- `200 OK` : Événement modifié
- `403 Forbidden` : L'événement est passé (non modifiable)
- `404 Not Found` : Événement inexistant

#### DELETE /events/{event_id}
Supprimer un événement

```bash
curl -X DELETE http://localhost:8000/events/3e9aa9c9-...
```

**Réponses** :
- `204 No Content` : Événement supprimé
- `403 Forbidden` : L'événement est passé (non supprimable)
- `404 Not Found` : Événement inexistant

## 📊 Structure des Données

### Modèle Event

```python
{
  "id": "uuid",                      # Identifiant unique
  "title": "string",                 # Libellé
  "description": "string|null",      # Notes
  "start": "ISO 8601 datetime",      # Date de début
  "end": "ISO 8601 datetime|null",   # Date de fin (optionnel)
  "color": "hex color",              # #RRGGBB (défaut: #28a745)
  "resources": ["string"],           # Liste de ressources (pods, serveurs)
  "rrule": "string|null",            # Règle de récurrence RRULE
  "all_day": "boolean",              # Événement toute la journée
  "created_at": "ISO 8601 datetime", # Timestamp de création
  "deleted_at": "ISO 8601 datetime|null"  # Soft delete (logique)
}
```

### Base de Données

**Table `events`** (PostgreSQL 16)

```sql
CREATE TABLE events (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR NOT NULL,
  description VARCHAR,
  start VARCHAR NOT NULL,
  end VARCHAR,
  color VARCHAR DEFAULT '#28a745',
  resources JSONB DEFAULT '[]'::jsonb,
  rrule VARCHAR,
  all_day BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP
);
```

## 🐳 Docker Compose

### Services

```yaml
postgres:
  # PostgreSQL 16 Alpine
  # Données: ./data/ (volume persistant)
  # Port: 5432
  # Healthcheck: pg_isready

backend:
  # FastAPI + Uvicorn
  # Mount statiques: ./static/
  # Port: 8000
  # Dépend de: postgres (service_healthy)
```

### Commandes Utiles

```bash
# Voir les logs
docker compose logs -f backend

# Accéder à PostgreSQL
docker compose exec postgres psql -U devops -d calendar

# Nettoyer (volumes inclus)
docker compose down -v

# Rebuild après modifications
docker compose build backend
docker compose restart backend
```

## 📋 Architecture

```
devops-calendar/
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── database.py          # Connexion AsyncPG + sessionmaker
│   ├── models.py            # Modèle SQLAlchemy Event
│   ├── schemas.py           # Pydantic schemas + validators
│   ├── crud.py              # Opérations DB asynchrones
│   ├── requirements.txt      # Dépendances Python
│   ├── Dockerfile           # Image backend
│   ├── routers/
│   │   └── events.py        # Endpoints API + validations 403
│   └── __init__.py
├── static/
│   └── index.html           # Frontend Bootstrap 5.3 + FullCalendar
├── data/                    # Volume PostgreSQL (gitignored)
├── docker-compose.yml       # Orchestration
└── README.md               # Cette documentation
```

## 🔐 Règles de Sécurité

### Validations Dates

| Scénario | Règle | Code |
|----------|-------|------|
| Créer un événement | start >= now + 15 min | 422 |
| Modifier un événement passé | Interdit | 403 |
| Supprimer un événement passé | Interdit | 403 |
| Heure locale | Utiliser TZ client | JS `datetime-local` |

### Soft Delete

Les événements supprimés ne sont **jamais** perdus, juste marqués `deleted_at`:
```sql
-- Les suppressions ne retournent que non-supprimés
WHERE deleted_at IS NULL
```

## 🧪 Tests API

### Créer un événement valide

```bash
# Demain à 18h (valide si maintenant < 17h45)
TOMORROW=$(date -d "+1 day" +"%Y-%m-%d")
curl -X POST http://localhost:8000/events/ \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Maintenance\",
    \"start\": \"${TOMORROW}T18:00:00\",
    \"color\": \"#dc3545\",
    \"resources\": [\"pod-01\"]
  }"
```

### Tenter de créer avec date passée (échouera)

```bash
curl -X POST http://localhost:8000/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Past Event",
    "start": "2025-12-01T10:00:00"
  }'
# Réponse: 422 Unprocessable Entity
# Erreur: "La date doit être au minimum dans 15 minutes"
```

## 📱 Responsive Design

- ✅ Desktop (calendrier complet)
- ✅ Tablette (modal fullscreen)
- ✅ Mobile (touches-friendly, paysage/portrait)

Bootstrap 5.3 garantit une expérience optimale sur tous les appareils.

## 🔄 Intégrations Futures

- [ ] Authentification (JWT / OAuth2)
- [ ] Webhooks pour notifications (Slack, Teams, etc.)
- [ ] Export iCalendar (.ics)
- [ ] Import depuis calendriers externes
- [ ] Alertes/rappels push
- [ ] Multi-utilisateurs avec permissions
- [ ] Analytics & rapports

## 📝 Notes de Développement

### Architecture Async

Le projet utilise **100% async**:
- FastAPI + Uvicorn (async handlers)
- SQLAlchemy 2.0 async ORM
- AsyncPG driver (PostgreSQL async)

### Fuseau Horaire

- **Backend** : Stockage en UTC pour cohérence
- **Frontend** : Affichage en heure locale (browser TZ)
- **Validation** : Comparaison en UTC

### Gestion des Erreurs

- Pydantic validators → 422 validation errors
- Router checks → 403 forbidden (events passés)
- CRUD failures → 404 not found
- Toasts Bootstrap → feedback utilisateur

## 📄 Licence

MIT

## 👤 Support

Pour toute question ou bug, ouvrir une issue sur le dépôt.

---

**Dernière mise à jour** : Janvier 2026  
**Status** : ✅ Production-ready
