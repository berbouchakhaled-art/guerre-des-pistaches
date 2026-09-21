# La guerre des pistaches — starring Sousou

Jeu navigateur gratuit. Ouvre `index.html` via **HTTP** (GitHub Pages ou un petit serveur local) — le chargement applique un polish sur la base du jeu et nécessite le réseau.

## Jouer

1. Ouvre [`index.html`](./index.html) dans un navigateur moderne (Chrome, Firefox, Safari) **via HTTP** (pas `file://`).
2. Choisis la difficulté (**Pour tous** / **Normal** / **Défi**) et un monde, ou lance **Histoire (1 → 2 → 3)**.
3. Sur iPhone / iPad : touche d’abord **Activer le son**, volume du téléphone +, interrupteur silencieux OFF.

Serveur local rapide : `python3 -m http.server 8080` puis http://localhost:8080/

## Contrôles

| Action | Clavier | Mobile |
|--------|---------|--------|
| Courir | ← → | Croix directionnelle |
| Sauter | Espace / Z / W | **SAUT** |
| Tirer | X / clic | **TIR** |
| Viser en haut | ↑ | ↑ |
| Se baisser | ↓ | ↓ |
| Armes | 1 / 2 / 3 ou Tab | Boutons 🗡️🔫💣 |
| Pause | P | — |
| Mute | M | Bouton 🔊 (mémorisé) |

## Mondes

1. **Parc Pistache** — jour, herbe, tuyaux  
2. **Nuit Cosmique** — espace, trampolines, étoiles  
3. **Vaisseau Pistache** — raisins secs aliens  

Thème 100 % pistaches (ennemis « cacahuètes » = vilains de cartoon uniquement).

## Polish (cette branche)

- Game feel : coyote time, jump buffer, hauteur de saut variable, particules / shake
- Invulnérabilité plus lisible, SFX plus nets, mute fiable + persistant
- HUD / overlays / indices première partie, écrans de fin plus clairs
- Mobile : touch-action, safe-area, anti zoom/scroll accidentel
- Correctif mode Histoire (messages de monde dynamiques)

## Notes techniques

- Aucune pub, analytics, compte ou API payante.
- Audio Web Audio API (déblocage au geste utilisateur).
- `index.html` charge la base pinnée (`main` @ `57ac0ae…`) puis applique `h00.hex`…`h05.hex` (patch gzip).
- Compatible tactile + safe-area + paysage.

Bon jeu — ★ SOUSOU ★
