from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from database import engine
from models import Base
from routers import events

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
app.mount("/static", StaticFiles(directory="/static"), name="static")

# Inclure les routers
app.include_router(events.router)

@app.get("/")
def root():
    return {"message": "DevOps FullCalendar API ✅"}
