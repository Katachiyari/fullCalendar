from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.database import engine
from app.models import Base, User, Event  # Import models
from app.routers import events, users, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Créer les tables au démarrage
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

# CORS pour le développement
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Servir les fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inclure les routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "DevOps FullCalendar API ✅"}
