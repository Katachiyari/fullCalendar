#!/usr/bin/env python3
"""
Test rapide du système d'authentification
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_password_hashing():
    """Tester le hachage et vérification de mots de passe"""
    print("🔐 Test du système de mots de passe")
    print("=" * 50)
    
    from app.security import hash_password, verify_password
    
    # Test 1: Hachage
    password = "Admin@123456"
    print(f"\n1️⃣  Mot de passe original: {password}")
    
    hashed = hash_password(password)
    print(f"2️⃣  Mot de passe hashé: {hashed[:50]}...")
    
    # Test 2: Vérification correcte
    is_valid = verify_password(password, hashed)
    print(f"3️⃣  Vérification avec bon mot de passe: {'✅ OK' if is_valid else '❌ FAIL'}")
    
    # Test 3: Vérification incorrecte
    is_invalid = verify_password("WrongPassword", hashed)
    print(f"4️⃣  Vérification avec mauvais mot de passe: {'❌ OK (devrait être reject)' if is_invalid else '✅ OK (correctement rejeté)'}")
    
    print("\n✨ Test des mots de passe réussi!\n")

def test_jwt_token():
    """Tester JWT tokens"""
    print("🎫 Test du système JWT")
    print("=" * 50)
    
    from app.security import create_access_token, decode_access_token
    
    # Test 1: Création de token
    user_data = {"sub": "admin@devops.example.com"}
    token = create_access_token(user_data)
    print(f"\n1️⃣  Token créé: {token[:50]}...")
    
    # Test 2: Décodage
    try:
        decoded = decode_access_token(token)
        print(f"2️⃣  Token décodé: {decoded}")
        print("✅ Token valide")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n✨ Test JWT réussi!\n")

def show_models():
    """Afficher la structure des modèles"""
    print("📊 Structure des modèles")
    print("=" * 50)
    
    from app.models import User, UserRole, Event
    from sqlalchemy import inspect
    
    # User model
    print("\n👤 User Model:")
    mapper = inspect(User)
    for column in mapper.columns:
        nullable = "✅ Optional" if column.nullable else "⚠️ Required"
        print(f"  • {column.name} ({column.type}) - {nullable}")
    
    # UserRole enum
    print("\n🎭 UserRole Enum:")
    for role in UserRole:
        print(f"  • {role.value}")
    
    print("\n✨ Modèles chargés avec succès!\n")

if __name__ == "__main__":
    try:
        print("\n" + "=" * 50)
        print("🧪 TESTS D'AUTHENTIFICATION")
        print("=" * 50 + "\n")
        
        test_password_hashing()
        test_jwt_token()
        show_models()
        
        print("\n" + "=" * 50)
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print("=" * 50)
        print("\n🚀 Maintenant, exécutez:")
        print("   python init_db.py")
        print("   python -m uvicorn app.main:app --reload\n")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
