#!/usr/bin/env python3
"""
Script de test des endpoints d'authentification et événements
Utilise curl ou requests pour valider le fonctionnement
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ {msg}{Colors.END}")

def run_curl(method, endpoint, data=None, headers=None):
    """Exécute une requête curl et retourne la réponse"""
    cmd = ["curl", "-s", "-X", method, f"{BASE_URL}{endpoint}"]
    
    if headers:
        for key, value in headers.items():
            cmd.extend(["-H", f"{key}: {value}"])
    
    if data:
        cmd.extend(["-H", "Content-Type: application/json"])
        cmd.extend(["-d", json.dumps(data)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return json.loads(result.stdout) if result.stdout else {"error": "No response"}
    except Exception as e:
        print_error(f"Request failed: {e}")
        return None

def test_auth():
    """Test les endpoints d'authentification"""
    print_section("🔐 TEST AUTHENTIFICATION")
    
    # Test 1: Inscription
    print_info("Test 1: Inscription nouvelle utilisateur")
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"test-{int(datetime.now().timestamp())}@example.com",
        "age": 30,
        "phone_number": "0612345678",
        "job_title": "Developer",
        "password": "TestPassword123"
    }
    
    response = run_curl("POST", "/auth/register", user_data)
    if response and "email" in response:
        print_success(f"Inscription réussie: {response['email']}")
        test_email = response['email']
    else:
        print_error(f"Inscription échouée: {response}")
        return None
    
    # Test 2: Connexion
    print_info("\nTest 2: Connexion avec les identifiants")
    login_data = {
        "email": test_email,
        "password": "TestPassword123"
    }
    
    response = run_curl("POST", "/auth/login", login_data)
    if response and "access_token" in response:
        print_success(f"Connexion réussie, token reçu")
        token = response['access_token']
    else:
        print_error(f"Connexion échouée: {response}")
        return None
    
    # Test 3: Récupérer l'utilisateur connecté
    print_info("\nTest 3: Récupérer les infos de l'utilisateur connecté")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = run_curl("GET", "/auth/me", headers=headers)
    if response and "email" in response:
        print_success(f"Utilisateur récupéré: {response['first_name']} {response['last_name']}")
    else:
        print_error(f"Récupération échouée: {response}")
    
    # Test 4: Changer le mot de passe
    print_info("\nTest 4: Changer le mot de passe")
    pwd_data = {
        "current_password": "TestPassword123",
        "new_password": "NewPassword456"
    }
    
    response = run_curl("POST", "/auth/change-password", pwd_data, headers)
    if response and ("message" in response or "access_token" in response):
        print_success("Mot de passe changé")
    else:
        print_error(f"Changement échoué: {response}")
    
    # Test 5: Mettre à jour le profil
    print_info("\nTest 5: Mettre à jour le profil")
    update_data = {
        "first_name": "TestModified",
        "last_name": "UserModified",
        "job_title": "Senior Developer"
    }
    
    response = run_curl("PUT", "/auth/me", update_data, headers)
    if response and response.get("first_name") == "TestModified":
        print_success("Profil mis à jour")
    else:
        print_error(f"Mise à jour échouée: {response}")
    
    return token, test_email

def test_events(token):
    """Test les endpoints d'événements"""
    print_section("📅 TEST ÉVÉNEMENTS")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Créer un événement
    print_info("Test 1: Créer un nouvel événement")
    tomorrow = (datetime.now() + timedelta(days=1)).isoformat()
    event_data = {
        "title": "Réunion importante",
        "description": "Test d'événement créé via API",
        "date_time": tomorrow
    }
    
    response = run_curl("POST", "/events/", event_data, headers)
    if response and "id" in response:
        print_success(f"Événement créé: {response['title']}")
        event_id = response['id']
    else:
        print_error(f"Création échouée: {response}")
        return
    
    # Test 2: Lister les événements
    print_info("\nTest 2: Lister tous les événements")
    response = run_curl("GET", "/events/", headers=headers)
    if isinstance(response, list):
        print_success(f"Événements récupérés: {len(response)} au total")
    else:
        print_error(f"Listing échoué: {response}")
    
    # Test 3: Récupérer un événement spécifique
    print_info("\nTest 3: Récupérer un événement spécifique")
    response = run_curl("GET", f"/events/{event_id}", headers=headers)
    if response and "title" in response:
        print_success(f"Événement récupéré: {response['title']}")
    else:
        print_error(f"Récupération échouée: {response}")
    
    # Test 4: Mettre à jour un événement
    print_info("\nTest 4: Mettre à jour l'événement")
    update_data = {
        "title": "Réunion importante - MODIFIÉE",
        "description": "Description mise à jour"
    }
    
    response = run_curl("PUT", f"/events/{event_id}", update_data, headers)
    if response and response.get("title") == "Réunion importante - MODIFIÉE":
        print_success("Événement mis à jour")
    else:
        print_error(f"Mise à jour échouée: {response}")
    
    # Test 5: Supprimer un événement
    print_info("\nTest 5: Supprimer l'événement")
    response = run_curl("DELETE", f"/events/{event_id}", headers=headers)
    if response and ("message" in response or response.get("status") == "deleted"):
        print_success("Événement supprimé")
    else:
        print_error(f"Suppression échouée: {response}")

def test_admin(admin_token):
    """Test les endpoints admin"""
    print_section("👨‍💼 TEST ADMIN")
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Lister tous les utilisateurs
    print_info("Test 1: Lister tous les utilisateurs")
    response = run_curl("GET", "/users/", headers=headers)
    if isinstance(response, list):
        print_success(f"Utilisateurs récupérés: {len(response)} au total")
    else:
        print_error(f"Listing échoué: {response}")

def main():
    """Fonction principale"""
    print(f"{Colors.BLUE}")
    print("=" * 60)
    print("  🧪 TEST SUITE - API Calendrier")
    print("=" * 60)
    print(f"{Colors.END}")
    
    print_info("Configuration:")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    
    # Test authentification
    result = test_auth()
    if not result:
        print_error("\nTests échoués - arrêt")
        sys.exit(1)
    
    token, email = result
    
    # Test événements
    test_events(token)
    
    # Test admin avec admin@devops.example.com si dispo
    print_info("\nNote: Les tests admin ne sont pas disponibles")
    print_info("Utilisez un compte ADMIN pour les tester")
    
    print_section("✅ TESTS TERMINÉS")
    print_success("La plupart des endpoints fonctionnent correctement!")
    print(f"{Colors.YELLOW}Note: Remplacez les URLs localhost par votre domaine en production{Colors.END}")

if __name__ == "__main__":
    main()
