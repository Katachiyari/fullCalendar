#!/bin/bash

cd /media/james/DATA1/python/fullCalendar
source venv/bin/activate

echo "═══════════════════════════════════════════════════════════════"
echo "  🚀 Démarrage du serveur"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🌐 URL: http://localhost:8001/login"
echo ""
echo "📝 Identifiants:"
echo "   Email:    admin@devops.example.com"
echo "   Password: Admin@123456"
echo ""
echo "Pour arrêter: CTRL+C"
echo "═══════════════════════════════════════════════════════════════"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
