#!/usr/bin/env python3
"""
Script d'initialisation rapide - Crée la DB et l'admin sans Docker
"""
import sys
import os
import asyncio

# Ajouter le chemin pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def init_db():
    """Initialiser la base de données"""
    print("📝 Initialisation de la base de données...")
    
    try:
        from app.database import engine
        from app.models import Base, User, Event  # IMPORTANT: Importer les modèles pour qu'ils soient enregistrés
        
        # Créer les tables
        print("   Tables détectées:", list(Base.metadata.tables.keys()))
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Tables créées avec succès")
        
        # Créer l'admin
        print("\n👤 Création de l'utilisateur admin...")
        from app.seed_admin import create_initial_admin
        await create_initial_admin()
        
        print("\n✨ Initialisation terminée!")
        print("\n🚀 Prochaines étapes:")
        print("   1. Démarrer l'app: python -m uvicorn app.main:app --reload")
        print("   2. Ouvrir: http://localhost:8000/static/login.html")
        print("   3. Email: admin@devops.example.com")
        print("   4. Mot de passe: Admin@123456")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(init_db())
