# Sousou — Dans la coque

Date : 2026-10-02. Statut : à relire avant tout code.

Ce document décrit la première tranche jouable de *La guerre des pistaches*. Elle ne remplace pas encore `index.html`. Elle ne part pas sur le game stick.

## Ce qu’on construit

Une page nouvelle, `coque.html`, à côté de `index.html`. Un seul niveau : l’intérieur d’une pistache géante. Sousou court, saute, s’accroche au caramel, tire une pistache, donne un coup de fouet.

`index.html` (tuyaux, blocs, drapeaux, lance, gun, grenade) reste tel quel. La ROM NES du stick n’est pas touchée.

## Sousou

Référence d’identité : `VISUEL SOUSOU.gif` dans le dossier RETRO GAMING. Dans le jeu, il n’est plus ce sprite pixel, ni le rendu 3D lisse. Il est dessiné comme le décor.

Traits fixes, visibles sur les cinq images :

- cheveux châtains ondulés
- t-shirt blanc classique, manches courtes, le bas passe sur la ceinture du jean, aucune peau à la taille
- jean bleu entier, des hanches aux baskets, aucune peau sur les jambes
- baskets rouges, semelles blanches
- contour noir épais, aplats, même épaisseur de trait que la coque

Images validées, dans `art/coque/` :

| Fichier | Pose |
| --- | --- |
| `debout.jpg` | Debout, portrait de base |
| `course.jpg` | Court vers la droite |
| `caramel.jpg` | En l’air, une main fermée sur un fil de caramel |
| `tir.jpg` | Debout, vise à droite, lance-noix, une pistache sort du canon |
| `fouet.jpg` | Debout, fouet dont le bout est une coque de pistache |

Ces fichiers sont la référence de style. Ce ne sont pas des sprites détourés. `coque.html` dessine Sousou en formes (aplats et contour noir), calées sur ces images. On ne découpe pas les JPEG pour en faire le personnage.

## Le niveau

Une salle, vue de côté, qui défile un peu avec Sousou. Elle reprend le décor de `debout.jpg` :

- coque verte autour d’un intérieur crème
- une fissure de lumière verte en haut
- des fils de caramel qui pendent du plafond
- une plateforme de sol sur toute la largeur
- trois plateformes d’amande : une basse à gauche, une au milieu, une à droite

Pas d’ennemis, pas de score, pas de vies, pas de raisins secs, pas de deuxième arme. La salle est vide à part Sousou, le décor, les fils et les pistaches qu’il tire.

Les pistaches tirées traversent l’écran et disparaissent au bord. Elles ne cassent rien dans cette tranche.

## Commandes

Clavier :

- flèches gauche et droite : marcher. La course de `course.jpg` est la marche tenue, pas une touche à part.
- Espace : saut. En l’air, si un fil de caramel est à portée de la main, Espace l’attrape. Sousou pend au fil. Les flèches le balancent à gauche ou à droite. Il lâche quand on relâche Espace. Sur la manette, c’est la croix qui balance, et on lâche en relâchant le bouton du bas.
- J : tir, comme `tir.jpg`. Une pistache à la fois en vol.
- L : fouet, comme `fouet.jpg`. Coup court devant lui.

Manette, nommée par la position des boutons (un pad Xbox appelle « A » ce qu’une Super Nintendo appelle « B ») :

- croix : gauche et droite
- bouton du bas : saut, et caramel en l’air
- bouton de gauche : tir
- bouton de droite : fouet

Pas de touche pour changer d’arme. Il n’y a que le lance-noix.

## Hors de cette tranche

- Le rayon, l’usine, le monde trash et son parachute
- Le game stick et la ROM NES
- La lance, le gun et la grenade de `index.html`
- Les ennemis

## Fait quand

On ouvre `coque.html`. Sousou a le t-shirt long, le jean entier, les baskets rouges et le trait de `art/coque/`. On peut courir, sauter, attraper un fil, tirer une pistache et donner un coup de fouet, au clavier et à la manette.
