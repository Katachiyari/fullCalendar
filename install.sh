#!/bin/bash
set -e  # Arrêter si erreur

echo "═══════════════════════════════════════════════════════════════"
echo "  Installation de l'environnement"
echo "═══════════════════════════════════════════════════════════════"
echo ""

cd /media/james/DATA1/python/fullCalendar

# 1. Supprimer l'ancien venv s'il existe
if [ -d "venv" ]; then
    echo "🗑️  Suppression de l'ancien environnement..."
    rm -rf venv
fi

# 2. Créer un nouvel environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv
echo "✓ Environnement créé"
echo ""

# 3. Activer et installer les dépendances
echo "📚 Installation des dépendances..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r app/requirements.txt --quiet
echo "✓ Dépendances installées"
echo ""

# 4. Vérifier les packages critiques
echo "🔍 Vérification des packages critiques..."
python -c "import fastapi; import uvicorn; import sqlalchemy; import jwt; import passlib; print('✓ Tous les packages sont installés')"
echo ""

# 5. Initialiser la base de données
echo "🗄️  Initialisation de la base de données..."
python init_db.py
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Installation terminée!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Pour démarrer le serveur, lancez:"
echo "  bash start.sh"
echo ""
