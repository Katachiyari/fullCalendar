"""
Script pour créer un utilisateur ADMIN initial avec JWT.
À exécuter une fois après le premier déploiement.

Usage:
  docker-compose exec app python seed_admin.py
  ou
  python app/seed_admin.py
"""
import asyncio
from app.database import SessionLocal
from app.models import User, UserRole
from app.security import hash_password
from sqlalchemy import select


async def create_initial_admin():
    """Créer un admin initial s'il n'y en a pas"""
    async with SessionLocal() as db:
        # Vérifier si un admin existe déjà
        result = await db.execute(select(User).where(User.role == UserRole.ADMIN))
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print(f"⚠️  Un admin existe déjà: {existing_admin.email}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role}")
            return
        
        # Créer un admin par défaut avec mot de passe hashé
        admin_password = "Admin@123456"  # ⚠️ À CHANGER EN PRODUCTION
        hashed_password = hash_password(admin_password)
        
        admin = User(
            first_name="Admin",
            last_name="System",
            email="admin@devops.example.com",
            phone_number="+33600000000",
            age=30,
            job_title="System Administrator",
            hashed_password=hashed_password,
            is_active=True,
            role=UserRole.ADMIN
        )
        
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        
        print("✅ Admin créé avec succès!")
        print(f"   Email: {admin.email}")
        print(f"   Password: {admin_password}")
        print(f"   Role: {admin.role}")
        print(f"\n💡 Utilisez ces identifiants pour vous connecter:")
        print(f"   URL: http://localhost:8000/static/login.html")
        print(f"   Email: {admin.email}")
        print(f"   Mot de passe: {admin_password}")

if __name__ == "__main__":
    asyncio.run(create_initial_admin())
