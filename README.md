# La guerre des pistaches — starring Sousou

Jeu navigateur gratuit (un seul fichier `index.html`). Ouvre le fichier localement (`file://` OK) ou via GitHub Pages.

## Jouer

1. Ouvre [`index.html`](./index.html) dans un navigateur moderne (Chrome, Firefox, Safari).
2. Choisis la difficulté (**Pour tous** / **Normal** / **Défi**) et un monde, ou lance **Histoire (1 → 2 → 3)**.
3. Sur iPhone / iPad : touche d’abord **Activer le son**, volume du téléphone +, interrupteur silencieux OFF.

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

## Portrait Sousou

- Menu : `assets/sousou-menu.png` (pixel art coloré transparent, rendu `pixelated`).
- En jeu : grand fond de map (`assets/sousou-bg.png`, upscale nearest-neighbor) derrière tous les mondes / histoire / difficultés — ~70% hauteur canvas, alpha ~0.38 (0.28 en lowFx), `imageSmoothingEnabled = false`.
- Perf légère : plafonds particules, culling hors écran, gradients ciel mis en cache, ombres réduites, mode FX allégé si FPS bas.

## Notes techniques

- Aucune pub, analytics, compte ou API payante.
- Audio Web Audio API (déblocage au geste utilisateur).
- Fichier unique autonome — aucun loader, aucun `h*.hex`, fonctionne hors ligne.
- Compatible tactile + safe-area + paysage.

Bon jeu — ★ SOUSOU ★
