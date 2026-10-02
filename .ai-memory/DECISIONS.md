# Décisions

Confirmées par l'utilisateur, dans l'ordre où elles comptent encore.

## Refus qui ferment une piste

- La ROM NES copiée sur le stick n'est pas son jeu. Nouveau refus le 2026-10-03 après test du rayon en pixels : ne plus proposer cette piste.
- Les trois mondes Mario (parc, nuit cosmique, vaisseau) ne sont pas la base. Pas un simple reskin.
- Pas un ver, pas d'armure verte, pas un enfant cartoon vert, pas le sprite cheveux courts de l'ancien `index.html`.
- Le dégradé « 3D doux » est refusé. Le jeu se dessine en aplats, contours noirs épais, comme le décor.
- Ne pas découper les JPEG en sprites. Les JPEG sont des références. Sousou en jeu est redessiné en formes.
- Pas de couloir en perspective, pas de vue isométrique. La caméra retenue est le profil d'Earthworm Jim : on court sur le sol, on saute sur les stands. Le sol est un plan, le stand a un dessus et une face.
- Les raisins ne sortent pas des boîtes et n'attaquent pas, dans Le rayon.
- Le parachute grossier n'existe que dans le monde trash, plus tard. Pas dans la coque, pas dans le rayon.
- Pas de seconde arme dans ces tranches. Pas de score, pas de vies, pas d'ennemis dans la coque ni dans la démo rayon.

## Identité de Sousou

Référence : `VISUEL SOUSOU.gif` (dossier RETRO GAMING, OneDrive). Cheveux bruns ondulés, t-shirt blanc assez long pour cacher la peau à la taille, jean bleu entier, baskets rouges semelles blanches. Plus présent que le gif, mêmes vêtements. Visage de la coque, de profil, dans le rayon.

Planches de référence coque, pas des sprites : `art/coque/debout.jpg`, `course.jpg`, `caramel.jpg`, `tir.jpg`, `fouet.jpg`.

## Mondes

1. Dans la coque. Validé (« je valide »), spécifié, planifié, codé. Spec : `docs/superpowers/specs/2026-10-02-sousou-coque-design.md`. Plan : `docs/superpowers/plans/2026-10-02-sousou-coque.md`.
2. Le rayon. Choisi par l'utilisateur. Gag : les étiquettes de prix jaunes servent d'accroche, comme le caramel. Première démo navigateur faite. Le fouet de la planche `rayon-fouet-2` a été accepté, puis il a demandé d'aller vite vers un test jouable.
3. L'usine à coques. Pas commencée.
4. Le monde trash, avec le parachute. Pas commencé.

## Coups

Course, saut, viser, tirer une pistache, fouet coquille, s'accrocher. Dans la coque l'accroche est le caramel. Dans le rayon c'est l'étiquette jaune.

Clavier : flèches, Espace saute et s'accroche, J tire, L fouet.
Manette, par position et pas par la lettre imprimée : bas = saut, gauche = tir, droite = fouet. Une manette branchée remplace le clavier.

Physique coque à ne pas casser si on y retouche : saut `JUMP = -22`, ordre du step (fouet, accroche, course, noix), une seule noix, pas de `ctx.scale`. Les tests l'épinglent.

## Le rayon, planches acceptées puis démo

Caméra A : courir au sol, sauter sur les comptoirs.
Course A. Accroche : le poing pince le bord droit de l'étiquette jaune du milieu, pieds au-dessus du bois, personnage plus petit que la course parce que l'étiquette est basse.
Tir A. Fouet A sur la seconde planche (corde lisible, grosse coque ouverte).
Ces planches sont des JPEG de travail dans `.superpowers/` (gitignoré), pas dans le runtime.

La démo `rayon.html` a réutilisé le petit sprite de la coque pour aller vite. Ce n'est pas le rendu des planches. L'utilisateur n'a pas dit que cette page navigateur était acceptée. Il a demandé le stick, a testé la ROM, et l'a refusée.
