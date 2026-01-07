<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Nous faisons dans le simple pour le moment :

Planification CI/CD : Visualisez et éditez les jobs GitLab CI (ex: builds, tests, deploys) via drag-and-drop ; API push les events depuis pipelines.​
Maintenance serveur : Calendrier des backups, restarts pods Swarm ou mises à jour Ansible ; coloré par criticité (vert=OK, rouge=urgent).​
Alertes monitoring : Intégrez Prometheus/Grafana pour afficher downtime ou pics CPU ; équipe notifiée via events récurrents.

C'est un labo, restons dans le simple. On a joutera des bricque comme Traefik ou autre plus tard.
il faut une base de données a part. PostGres et integrer SQLAlchemy

Prometheus/Grafana ne sont pas encore présent, mais ils sont a venir, donc nous pouvons anticipés

Il faut integrer fat API egalement
repense le cahier des charges détaillé.
Et établis un pas a pas.

Voici un cahier des charges simplifié pour votre labo DevOps : dashboard FullCalendar basique avec CRUD via FastAPI/SQLAlchemy/PostgreSQL, en Docker Compose mono-nœud. Focus sur planification CI/CD, maintenance et alertes futures (Prometheus-ready). Pas de Traefik/Swarm pour l'instant, évolutif.[^1][^2]

## Cahier des charges allégé

**Fonctionnalités MVP** :

- Calendrier FullCalendar (vues mois/semaine, drag-drop) : events pour jobs GitLab (build/deploy), maintenance (backup/restart), alertes mock.
- CRUD API : POST/PUT/GET/DELETE events (title, start/end, color=vert/jaune/rouge, desc).
- DB : PostgreSQL + SQLAlchemy ORM async.
**Évolutions prévues** : Webhooks GitLab/Prometheus push auto-events.
**Non-fonc.** : Localhost:80/8000, no auth (labo), logs console.[^3]


## Arborescence projet

```
devops-calendar/
├── docker-compose.yml
├── frontend/          # Nginx static
│   └── index.html     # FullCalendar JS
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   └── database.py
│   ├── requirements.txt
│   └── Dockerfile
└── init.sql          # DB schema
```


## Pas à pas implémentation

1. **Init projet** : `mkdir devops-calendar && cd devops-calendar`. Créez dossiers frontend/backend.[^4]
2. **Backend FastAPI** :
    - requirements.txt : `fastapi uvicorn sqlalchemy asyncpg psycopg2-binary pydantic`.
    - models.py :

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    start = Column(DateTime)
    end = Column(DateTime)
    color = Column(String)  # vert,rouge
    desc = Column(String)
```

    - database.py : Engine asyncpg `postgresql://user:pass@postgres:5432/db`.
    - main.py :

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
app = FastAPI()
@app.get("/events") def get_events(db: Session = Depends(get_db)): ...
@app.post("/events") def create_event(event: EventCreate, db: Session = Depends(get_db)): ...
```

    - Dockerfile : `FROM python:3.12-slim COPY . /app RUN pip install -r requirements.txt CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]`.[^1][^3]
```
3. **Frontend Nginx** : Téléchargez fullcalendar.io/dist, index.html avec `<script src="fullcalendar.js"></script> calendar.addEventSource('/events');`.[^5]
```

4. **DB init** : init.sql `CREATE TABLE events (...); INSERT SAMPLE DATA;`.[^2]
5. **Docker Compose** :

```
services:
  postgres:
    image: postgres:16
    environment: POSTGRES_DB: calendar_db, POSTGRES_USER: user, POSTGRES_PASSWORD: pass
    volumes: ['./init.sql:/docker-entrypoint-initdb.d/init.sql']
    ports: ['5432:5432']
  backend:
    build: ./backend
    depends_on: [postgres]
    ports: ['8000:8000']
    environment: DATABASE_URL: postgresql://user:pass@postgres:5432/calendar_db
  frontend:
    image: nginx:alpine
    volumes: ['./frontend:/usr/share/nginx/html:ro']
    ports: ['80:80']
```

Lancez `docker compose up -d`. Accès http://localhost (calendar) /docs (API).[^6][^4]
6. **Tests** : Curl POST event, vérifiez DB/UI. Ajoutez mock GitLab webhook endpoint.[^7]

## Anticipation évolutions

- Ajout endpoint `/webhook/gitlab` pour push pipeline events.
- Middleware Prometheus FastAPI pour métriques futures Grafana.
- Migrate vers Compose override pour Swarm/Traefik.[^8]

<div align="center">⁂</div>

[^1]: https://fastapi.tiangolo.com/deployment/docker/

[^2]: https://fastapi.tiangolo.com/tutorial/sql-databases/

[^3]: https://tutlinks.com/fastapi-with-postgresql-crud-async/

[^4]: https://www.digitalocean.com/community/tutorials/create-fastapi-app-using-docker-compose

[^5]: https://fullcalendar.io

[^6]: https://stackoverflow.com/questions/75140541/fastapi-served-through-nginx-with-gunicorn-and-docker-compose

[^7]: https://www.youtube.com/watch?v=8X1mWuhmOAg

[^8]: https://testdriven.io/blog/fastapi-docker-traefik/

