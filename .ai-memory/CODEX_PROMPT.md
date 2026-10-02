Tu reprends Sousou, « La guerre des pistaches », à la place de Grok. Lis d'abord la boîte noire, dans cet ordre, puis seulement le code qu'elle cite :

1. AGENTS.md
2. .ai-memory/PROJECT_STATE.md
3. .ai-memory/CURRENT_TASK.md
4. .ai-memory/DECISIONS.md
5. .ai-memory/HANDOFF.md
6. .ai-memory/OPEN_QUESTIONS.md
7. .ai-memory/ARCHITECTURE.md

Dépôt : https://github.com/berbouchakhaled-art/guerre-des-pistaches
Branche de travail : sousou-coque
Worktree local s'il est encore là : /Users/test/Desktop/pistache-soldat/.worktrees/sousou-coque

La branche main de GitHub est l'ancien jeu (trois mondes façon Mario, GitHub Pages). L'utilisateur a dit que ce n'est pas la base. N'y touche pas, ne remplace pas index.html, ne force-push pas, ne lance pas les workflows pixel.

La branche nes-rayon-rejete est une archive. Le 3 octobre 2026 il a testé cette ROM sur son Game Stick et l'a refusée entièrement. Ce n'était pas son jeu. Interdit de l'améliorer, de la régénérer, de la recopier sur la clé, ou de proposer une autre ROM « en attendant ». Le stick ne lance que des ROM et ne peut pas ouvrir la page. On ne règle pas ça dans cette reprise.

Ce qu'il faut faire : Le rayon, dans le navigateur, jouable, au dessin des planches déjà acceptées. Pas le petit sprite recopié depuis la coque. Pas un collage des JPEG. Sousou est redessiné en formes canvas : cheveux bruns ondulés, t-shirt blanc long, jean bleu, baskets rouges semelles blanches, contour noir épais, aplats. Profil. Il court sur le sol, saute sur trois comptoirs, s'accroche à une étiquette jaune, tire une pistache, donne un coup de fouet coquille. Les raisins restent dans les boîtes. Pas de score, pas de vies, pas d'ennemis, pas de seconde arme.

Contrôles déjà fixés. Clavier : flèches, Espace saute et s'accroche, J tire, L fouet. Manette par position : bas saute, gauche tire, droite fouet. Une manette branchée remplace le clavier.

La coque (coque.html, coque/) est une tranche à part, déjà testée (node --test coque/logic.test.mjs coque/input.test.mjs coque/draw.test.mjs). Ne la casse pas. Ne la prends pas comme le modèle de taille du personnage du rayon : dans le rayon il était trop petit, et c'est pour ça que l'écran ne lui ressemble pas.

Sers la page avec un serveur HTTP. file:// casse les modules. Vérifie dans le navigateur : course, saut sur un comptoir, accroche, tir, fouet. Dis ce que tu as vraiment vu.

Pas de Docker : ce jeu n'en a pas. Ne pas merger. Ne pas pousser main. Si tu commits, reste sur sousou-coque. Avant de t'arrêter, mets à jour .ai-memory/CURRENT_TASK.md et HANDOFF.md.

Parle-lui en français. Montre-lui la page, pas une ROM.
