# État du projet

Dernière mise à jour : 2026-10-03, après le test stick refusé par l'utilisateur.

## Produit

Sousou, dans « La guerre des pistaches ». Le but est un jeu qu'on sent comme Earthworm Jim 2 (mondes, dessin, prise en main), sans copier ses images ni ses niveaux. L'humour est la nourriture. Le personnage n'est pas un ver.

L'utilisateur vient de tester la ROM NES mise sur le Game Stick. Il l'a refusée entièrement. Ce n'est pas une base à améliorer. Ne pas la réinstaller, ne pas la « pixeliser mieux », ne pas y ajouter des frames.

## Deux historiques Git qui ne sont pas le même jeu

- GitHub `berbouchakhaled-art/guerre-des-pistaches`, branche `main` (`9432dca` au 25 sept. 2026, plus le commit de cette boîte noire). C'est l'ancien jeu navigateur : trois mondes façon Mario (parc, cosmos, vaisseau), pipeline pixel, GitHub Pages. L'utilisateur a dit que ces trois mondes ne sont pas la base. Ne pas écraser `index.html`. Ne pas force-push.
- Branche `sousou-coque`. Historique local séparé (commit racine `ec0e61d`), worktree `/Users/test/Desktop/pistache-soldat/.worktrees/sousou-coque`. C'est là qu'est la tranche jouable nouvelle. Ne pas la fusionner dans `main` tant que l'utilisateur ne le demande pas.
- Branche `nes-rayon-rejete`. La ROM du rayon refusée le 3 oct. 2026. Archive, pas une suite.

## Ce qui se joue vraiment

- `coque.html` : « Dans la coque », tranche validée puis codée. 22 tests `node --test coque/*.test.mjs` au dernier passage connu. Clavier et manette.
- `rayon.html` : première démo navigateur du rayon (courir, sauter sur trois comptoirs, étiquette jaune, tir, fouet). Le sprite est celui, petit, de la coque. Les planches validées sont plus grandes et ne sont pas dans le jeu.
- Page GitHub Pages : l'ancien jeu. Elle n'a pas été remplacée.

## Stick

Le stick « NO NAME » ne lance que des ROM. Il ne peut pas ouvrir `rayon.html`. La ROM refusée est encore dans les Favoris sous le nom « La guerre des pistaches », dossier `001/`. La clé a été éjectée après la copie. Ne plus y toucher sans un oui explicite.

## Docker

Il n'y a pas de Docker sur ce jeu. Ne pas en ajouter. Le public est GitHub Pages (legacy), à partir de `main`. Les workflows dans `.github/workflows/` régénèrent des assets pixel sur d'autres branches. Ne pas les lancer pour cette reprise.
