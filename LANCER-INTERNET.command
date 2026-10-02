#!/bin/bash
# Rend le jeu accessible depuis n'importe quel mobile (3G/4G/5G)
# via un lien HTTPS public Cloudflare.
cd "$(dirname "$0")"
PORT=8080

echo ""
echo "=============================================="
echo "  LA GUERRE DES PISTACHES — Lien Internet"
echo "=============================================="
echo ""
echo "1) Garde cette fenêtre OUVERTE"
echo "2) Un lien https://....trycloudflare.com va s'afficher"
echo "3) Ouvre ce lien sur n'importe quel téléphone (4G OK)"
echo ""
echo "Ctrl+C pour tout arrêter"
echo "=============================================="
echo ""

# Libère le port si besoin
lsof -ti:"$PORT" | xargs kill -9 2>/dev/null || true

# Serveur local
python3 -m http.server "$PORT" &
SERVER_PID=$!
sleep 1

cleanup() {
  echo ""
  echo "Arrêt..."
  kill "$SERVER_PID" 2>/dev/null
  kill "$TUNNEL_PID" 2>/dev/null
  exit 0
}
trap cleanup INT TERM

# Tunnel public (HTTPS) — marche en 3G/4G partout dans le monde
npx --yes cloudflared tunnel --url "http://127.0.0.1:$PORT" &
TUNNEL_PID=$!

wait
