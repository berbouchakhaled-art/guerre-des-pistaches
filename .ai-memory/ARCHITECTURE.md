# Architecture

## Tranche nouvelle (`sousou-coque`)

Navigateur, modules ES, sans framework ni build.

- `coque.html`, `coque/logic.mjs`, `coque/input.mjs`, `coque/draw.mjs`, `coque/main.mjs`. Canvas 1280×720, monde 1600×720, sol y=620. Tests à côté des modules.
- `rayon.html`, `rayon/*`. Copie de la coque avec un autre décor, d'autres plateformes, une accroche étiquette. Monde 1600×720, sol y=560. Pas de tests rayon.
- `y` est la semelle, `x` le centre, `face` vaut 1 ou -1.
- `index.html` de cette branche est l'ancien jeu local de la baseline `ec0e61d`. Ne pas le prendre pour la cible.

## Jeu GitHub `main`

`index.html` + `js/` + `css/` + `assets/` + `tools/gfx`. C'est l'ancien produit Pages. Le lire pour ne pas le confondre avec Sousou, pas pour le continuer comme direction.

## ROM

`nes/build_rom.py` écrit une NROM de 24592 octets. La version rayon est sur `nes-rayon-rejete` seulement. Le générateur encore présent sur `sousou-coque` est l'ancienne démo trois mondes, déjà refusée avant le rayon.

## Ce qui n'existe pas

Pas de Docker, pas de Compose, pas de serveur d'application. Un `python3 -m http.server` suffit pour les modules ES. `file://` casse les imports.
