from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
from app.database import engine
from app.models import Base, User, Event, Group  # Import models
from app.routers import events, users, auth, groups, server, ansible
from app.v2.routers import alerts as v2_alerts
from app.v2.routers import calendar as v2_calendar
from app.v2.routers import pipeline as v2_pipeline
from app.v2.routers import projects as v2_projects
from app.v2.routers import sprints as v2_sprints
from app.v2.routers import tasks as v2_tasks
from app.v2.routers import tickets as v2_tickets
from app.db_migrations import apply_best_effort_migrations
from app.seed_groups import ensure_default_groups
from app.seed_admin import create_initial_admin
from app.v2.seed_demo import ensure_demo_v2_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Migrations légères (ajout colonnes) puis création des tables
    await apply_best_effort_migrations(engine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Groupes métiers par défaut
    from app.database import SessionLocal
    async with SessionLocal() as db:
        await ensure_default_groups(db)
        await ensure_demo_v2_data(db)

    # Admin par défaut (utile en dev / demo). Ne recrée pas si déjà présent.
    await create_initial_admin()
    yield

app = FastAPI(lifespan=lifespan)

# CORS pour le développement
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Une seule application front: on ne sert plus l'UI legacy en HTML sous /static.
# (On garde la SPA v2/v3 servie par FastAPI, et on redirige /static/* pour compat.)

@app.get("/static/{path:path}", include_in_schema=False)
def legacy_static_redirect(path: str):
    # Anciennes pages: login.html, index.html, admin-users.html, etc.
    # On redirige vers la SPA (une seule UI).
    return RedirectResponse(url="/", status_code=307)

# Servir les assets du frontend v2 (Vite build)
V2_DIST_DIR = os.getenv("V2_DIST_DIR", "v2_dist")
if os.path.isdir(os.path.join(V2_DIST_DIR, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(V2_DIST_DIR, "assets")), name="v2-assets")

# Inclure les routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(server.router)
app.include_router(ansible.router)

# v2 (DevOps project manager)
app.include_router(v2_tasks.router)
app.include_router(v2_alerts.router)
app.include_router(v2_pipeline.router)
app.include_router(v2_calendar.router)
app.include_router(v2_projects.router)
app.include_router(v2_sprints.router)
app.include_router(v2_tickets.router)

@app.get("/", include_in_schema=False)
def root():
    index_path = os.path.join(V2_DIST_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"message": "DevOps FullCalendar API ✅"}


@app.head("/", include_in_schema=False)
def root_head():
    index_path = os.path.join(V2_DIST_DIR, "index.html")
    if os.path.isfile(index_path):
        return Response(status_code=200, media_type="text/html")
    return Response(status_code=200, media_type="application/json")


@app.get("/{full_path:path}", include_in_schema=False)
def spa_fallback(full_path: str):
    # Les routes API, /static, /docs, /openapi.json, /assets, etc. seront déjà matchées avant.
    candidate = os.path.join(V2_DIST_DIR, full_path)
    if full_path and os.path.isfile(candidate):
        return FileResponse(candidate)

    index_path = os.path.join(V2_DIST_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)

    return {"detail": "Not Found"}
