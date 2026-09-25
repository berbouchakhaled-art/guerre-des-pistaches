"""Branche le moteur pixel-art (js/gfx.js) dans index.html via de petits hooks.
Idempotent : ne fait rien si index.html charge déjà js/gfx.js.
Usage : python3 tools/gfx/patch_index.py index.html"""
import sys, re
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
if 'src="js/gfx.js"' in s:
    print('already patched'); sys.exit(0)
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        raise SystemExit('pattern count %d != %d: %r' % (n, count, old[:80]))
    s = s.replace(old, new)
# CSS : rendu pixel net + HUD canvas
rep("""      cursor: crosshair;
      background: #5dade2;
      touch-action: none;
    }""", """      cursor: crosshair;
      background: #5dade2;
      touch-action: none;
      image-rendering: pixelated;
      image-rendering: crisp-edges;
    }
    /* HUD pixel dessiné dans le canvas (js/gfx.js) : on masque l'ancien HUD HTML */
    body.gfx-hud .hud { display: none !important; }""")
rep("La star aux cheveux courts", "La star aux cheveux ondulés")
rep("  <script>\n", "  <script src=\"js/gfx.js\"></script>\n  <script>\n")
rep("  const ctx = canvas.getContext('2d');\n", "  const ctx = canvas.getContext('2d');\n  ctx.imageSmoothingEnabled = false;\n")
# fond
rep("  function drawSousouMapBackground() {\n", "  function drawSousouMapBackground() {\n    if (window.GFX && GFX.skipSousouOnce) { GFX.skipSousouOnce = false; return; }\n")
rep("    if (levelDef.theme === 'ship') {\n      // Espace profond", "    ctx.imageSmoothingEnabled = false;\n    if (window.GFX && GFX.drawBackground(ctx)) {\n      // fond pixel-art parallaxe (js/gfx.js)\n    } else if (levelDef.theme === 'ship') {\n      // Espace profond")
# hooks de dessin
hooks = [
  ("  function drawTiles() {\n", "    if (window.GFX && GFX.drawTiles(ctx)) return;\n"),
  ("  function drawFlag() {\n", "    if (window.GFX && GFX.drawGoal(ctx)) return;\n"),
  ("  function drawCoin(c) {\n", "    if (window.GFX && GFX.drawCoin(ctx, c)) return;\n"),
  ("  function drawBullet(b) {\n", "    if (window.GFX && GFX.drawBullet(ctx, b)) return;\n"),
  ("  function drawEnemy(e) {\n", "    if (window.GFX && GFX.drawEnemy(ctx, e)) return;\n"),
  ("  function drawSousou() {\n", "    if (window.GFX && GFX.drawPlayer(ctx)) return;\n"),
  ("  function drawPowerup(p) {\n", "    if (window.GFX && GFX.drawPowerup(ctx, p)) return;\n"),
  ("  function drawMine(m) {\n", "    if (window.GFX && GFX.drawMine(ctx, m)) return;\n"),
  ("  function drawMeteor(m) {\n", "    if (window.GFX && GFX.drawMeteor(ctx, m)) return;\n"),
]
for a, b in hooks:
    rep(a, a + b)
# particules + fx sprites
rep("""    for (const p of particles) {
      if (!inViewXY(p.x, p.y, 40)) continue;
      ctx.globalAlpha = Math.min(1, p.life / 15);
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    }""", """    if (window.GFX) GFX.drawFx(ctx);
    if (!(window.GFX && GFX.drawParticles(ctx))) for (const p of particles) {
      if (!inViewXY(p.x, p.y, 40)) continue;
      ctx.globalAlpha = Math.min(1, p.life / 15);
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    }""")
rep("""      if (!inViewXY(f.x, f.y, 20)) continue;
      ctx.globalAlpha = Math.min(1, f.life / 20);
      ctx.fillStyle = '#fff59d';""", """      if (!inViewXY(f.x, f.y, 20)) continue;
      if (window.GFX && GFX.drawFloat(ctx, f)) continue;
      ctx.globalAlpha = Math.min(1, f.life / 20);
      ctx.fillStyle = '#fff59d';""")
# HUD pixel (remplace watermark + barre de buffs)
rep("""    // watermark + buffs actifs
    if (running && !paused) {""", """    // watermark + buffs actifs
    if (running && !paused && window.GFX && GFX.drawHud(ctx)) {
      // HUD pixel-art (js/gfx.js)
    } else if (running && !paused) {""")
# évènements cosmétiques
rep("    shootCD = cd;\n    const dir = player.facing;\n", "    shootCD = cd;\n    if (window.GFX) GFX.onShoot();\n    const dir = player.facing;\n")
rep("""    lives -= difficulty.contactLivesLost || 1;
    invuln = difficulty.invulnHit;
    screenShake = 14;""", """    lives -= difficulty.contactLivesLost || 1;
    invuln = difficulty.invulnHit;
    if (window.GFX) GFX.onHurt();
    screenShake = 14;""")
rep("""        if (hitSolid) { AudioFX.shellCrack(); explode(b.x, b.y, '#aed581', 6); }""",
    """        if (hitSolid) { AudioFX.shellCrack(); explode(b.x, b.y, '#aed581', 6); if (window.GFX) GFX.spawnFx('hit', b.x, b.y, 0.8); }""")
rep("""          e.hp -= b.dmg || 1;
""", """          e.hp -= b.dmg || 1;
          e.hitT = 8;
          if (window.GFX) GFX.spawnFx(b.kind === 'gun' ? 'hitOrange' : 'hit', b.x, b.y, b.r > 18 ? 1.6 : 1);
""")
rep("""  function explodeGrenade(x, y) {
""", """  function explodeGrenade(x, y) {
    if (window.GFX) GFX.spawnFx('boom', x, y, 2);
""")
rep("""  function squashEnemy(e, stomped) {
    e.flat = true;
""", """  function squashEnemy(e, stomped) {
    e.flat = true;
    e.shot = !stomped;
""")
rep("""      if (!c.pop && Math.hypot(player.x - c.x, (player.y - player.h / 2) - cy) < 44) {
        c.taken = true;
""", """      if (!c.pop && Math.hypot(player.x - c.x, (player.y - player.h / 2) - cy) < 44) {
        c.taken = true;
        if (window.GFX) GFX.spawnFx('spark', c.x, cy, 1.5);
""")
open(p, 'w', encoding='utf-8').write(s)
print('patched OK')
