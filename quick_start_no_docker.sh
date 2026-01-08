#!/bin/bash

# 🚀 DÉMARRAGE RAPIDE - SANS DOCKER

clear

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         🚀 DÉMARRAGE RAPIDE - CALENDRIER JWT                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd /media/james/DATA1/python/fullCalendar

echo "📋 ÉTAPES:"
echo ""
echo "1️⃣  Installer les dépendances..."
pip install -r app/requirements.txt

echo ""
echo "2️⃣  Initialiser la base de données et créer l'admin..."
python init_db.py

echo ""
echo "3️⃣  Lancer l'API (Terminal 1)..."
echo "    $ python -m uvicorn app.main:app --reload"
echo ""
echo "    [OUVRIR DANS UN AUTRE TERMINAL]"
echo ""
echo "4️⃣  Ouvrir le navigateur (Terminal 2)..."
echo "    $ xdg-open http://localhost:8000/login"
echo ""
echo "5️⃣  Utiliser les identifiants:"
echo "    Email:    admin@devops.example.com"
echo "    Password: Admin@123456"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🔗 URLs Importantes:"
echo "   • Login:    http://localhost:8000/login"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Profile:  http://localhost:8000/profile"
echo ""
echo "🧪 Tester les endpoints:"
echo "   $ python test_auth_system.py"
echo "   $ python test_api.py"
echo ""
echo "════════════════════════════════════════════════════════════"
