#!/bin/bash
# Lance un serveur local pour jouer sur iPhone (même Wi‑Fi)
cd "$(dirname "$0")"
PORT=8080
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "IP_INTROUVABLE")

echo ""
echo "=========================================="
echo "  LA GUERRE DES PISTACHES — iPhone"
echo "=========================================="
echo ""
echo "1) Garde cette fenêtre ouverte"
echo "2) Sur l'iPhone (même Wi‑Fi), ouvre Safari :"
echo ""
echo "   http://$IP:$PORT"
echo ""
echo "3) Appuie sur GO SOUSOU (paysage conseillé)"
echo ""
echo "Ctrl+C pour arrêter le serveur"
echo "=========================================="
echo ""

# Ouvre aussi sur le Mac
open "http://127.0.0.1:$PORT" 2>/dev/null

python3 -m http.server "$PORT"
