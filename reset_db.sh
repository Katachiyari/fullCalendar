#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "  🔄 Réinitialisation complète de la base de données"
echo "═══════════════════════════════════════════════════════════════"

cd /media/james/DATA1/python/fullCalendar

# 1. Arrêter le serveur s'il tourne (port 18000)
# echo "🛑 Arrêt des processus existants..."
# pkill -f uvicorn || true

# 2. Supprimer la DB existante
echo "🗑️  Suppression de calendar.db..."
rm -f calendar.db

# 3. Initialiser proprement
echo "🆕 Re-création de la base et de l'admin..."
source venv/bin/activate
python init_db.py

echo ""
echo "✅ Base de données réinitialisée!"
echo "➡️  Login: admin@devops.example.com"
echo "➡️  Pass:  Admin@123456"
echo ""
echo "Relancez le serveur maintenant:"
echo "bash start.sh"
