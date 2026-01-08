import asyncio
from app.database import async_session
from app.models import User
from sqlalchemy import select
from app.security import verify_password

async def check_admin():
    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == "admin@devops.example.com"))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"✅ Admin found: {user.email}")
            print(f"   Role: {user.role}")
            print(f"   Is Active: {user.is_active}")
            print(f"   Hashed Password: {user.hashed_password[:10]}...")
            
            # Test password verification
            is_valid = verify_password("Admin@123456", user.hashed_password)
            if is_valid:
                print("✅ Password 'Admin@123456' is VALID")
            else:
                print("❌ Password 'Admin@123456' is INVALID")
        else:
            print("❌ Admin user NOT found in database")

if __name__ == "__main__":
    asyncio.run(check_admin())
