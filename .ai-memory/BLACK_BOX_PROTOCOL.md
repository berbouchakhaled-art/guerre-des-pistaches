# Protocole de la boîte noire

Dernière mise à jour : 2026-10-03

## Début de session

1. `AGENTS.md`
2. `.ai-memory/PROJECT_STATE.md`
3. `.ai-memory/CURRENT_TASK.md`
4. `.ai-memory/DECISIONS.md`
5. `.ai-memory/HANDOFF.md`
6. `.ai-memory/OPEN_QUESTIONS.md`

Puis inspecter le code cité, pas un autre jeu.

## Trois niveaux

- Décision confirmée : validée par l'utilisateur.
- Hypothèse de travail : utile, pas encore confirmée.
- Question ouverte : à trancher avant un choix lourd.

## Fin de session

Mettre à jour `CURRENT_TASK.md`, `HANDOFF.md`, et si besoin `DECISIONS.md`, `OPEN_QUESTIONS.md`, `SOURCES.md`.

Format d'un passage de `HANDOFF.md` :

```md
## Session YYYY-MM-DD

Changed:
- ...

Verified:
- ...

Still open:
- ...

Next recommended step:
- ...
```
