# Protocole agent — La guerre des pistaches

Ce dépôt utilise `.ai-memory/` comme boîte noire. Elle fait foi pour Codex, Claude Code, Grok et tout autre agent.

Avant de modifier le code, la config ou la doc :

1. Lire `.ai-memory/PROJECT_STATE.md`.
2. Lire `.ai-memory/CURRENT_TASK.md`.
3. Lire `.ai-memory/DECISIONS.md`.
4. Lire `.ai-memory/HANDOFF.md`.
5. Lire `.ai-memory/OPEN_QUESTIONS.md`.

Pendant le travail :

- Ne pas inventer une direction que l'utilisateur a déjà refusée.
- Ne pas stocker de secrets, jetons, cookies ou données personnelles dans `.ai-memory/`.
- Écrire un point court dans `.ai-memory/HANDOFF.md` avant une longue implémentation.
- Si le contexte manque, s'arrêter et mettre à jour `CURRENT_TASK.md` puis `HANDOFF.md` avant d'arrêter.

Avant de s'arrêter :

1. Mettre à jour `.ai-memory/CURRENT_TASK.md`.
2. Mettre à jour `.ai-memory/HANDOFF.md`.
3. Ajouter toute décision durable dans `.ai-memory/DECISIONS.md`.
4. Ajouter toute question ouverte dans `.ai-memory/OPEN_QUESTIONS.md`.

Si le contexte manque, lire la boîte noire, puis le dépôt. Ne pas repartir d'une supposition.
