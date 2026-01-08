#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "  🚀 Configuration de l'application Calendar"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Vérifier qu'on est dans le bon dossier
cd /media/james/DATA1/python/fullCalendar

# 1. Créer l'environnement virtuel s'il n'existe pas
echo "📦 Étape 1: Créer l'environnement virtuel..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Environnement créé"
else
    echo "✓ Environnement existant"
fi
echo ""

# 2. Activer et installer les dépendances
echo "📚 Étape 2: Installer les dépendances (peut prendre 2-3 minutes)..."
source venv/bin/activate
pip install -q -r app/requirements.txt
echo "✓ Dépendances installées"
echo ""

# 3. Initialiser la base de données
echo "🗄️  Étape 3: Créer la base de données..."
python init_db.py
echo "✓ Base de données créée"
echo ""

# 4. Lancer le serveur
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Prêt!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Le serveur démarre sur: http://localhost:8000"
echo ""
echo "📝 Login avec:"
echo "   Email:    admin@devops.example.com"
echo "   Password: Admin@123456"
echo ""
echo "🔗 Calendrier: http://localhost:8000/static/login.html"
echo ""
echo "Pour arrêter: Appuyez sur CTRL+C"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# 5. Lancer le serveur
python -m uvicorn app.main:app --reload
