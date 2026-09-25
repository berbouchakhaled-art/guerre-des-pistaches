/* =====================================================================
 * La Guerre des Pistaches — moteur de rendu PIXEL-ART (phase 2)
 * ---------------------------------------------------------------------
 * Toutes les images sont générées par tools/gfx/*.py (Pillow, déterministe)
 * dans assets/gfx/ + assets/sousou-sprite.png (sprite officiel de Sousou).
 * index.html appelle ces fonctions via des "hooks" : si une image manque,
 * la fonction renvoie false et l'ancien rendu vectoriel prend le relais.
 * Aucun impact sur la physique : lecture seule de l'état du jeu
 * (sauf champs cosmétiques player.shootT / player.hurtT / e.hitT / b._tr).
 * ===================================================================== */
(function () {
  'use strict';
  const BASE = 'assets/';
  const G = {
    ready: false,
    img: {},
    failed: {},
    fx: [],
    skipSousouOnce: false,
  };
  window.GFX = G;

  // ---------------------------------------------------------------
  // Table des frames du sprite Sousou (assets/sousou-sprite.png, 288x192)
  // cellule 48x64, pieds sur la ligne du bas, centre du corps x=22
  // ---------------------------------------------------------------
  const SP = { w: 48, h: 64, ax: 22, ay: 64 };
  const SP_FRAMES = {
    idle_0: [0, 0], idle_1: [48, 0], idle_2: [96, 0], idle_3: [144, 0],
    run_0: [192, 0], run_1: [240, 0], run_2: [0, 64], run_3: [48, 64],
    run_4: [96, 64], run_5: [144, 64], jump: [192, 64], fall: [240, 64],
    shoot_0: [0, 128], shoot_1: [48, 128], blink: [96, 128], hurt: [144, 128],
  };
  const SP_ANIMS = {
    idle: ['idle_0', 'idle_1', 'idle_2', 'idle_3'],
    run: ['run_0', 'run_1', 'run_2', 'run_3', 'run_4', 'run_5'],
    shoot: ['shoot_0', 'shoot_1'],
  };

  const FILES = {
    sousou: 'sousou-sprite.png',
    items: 'gfx/items.png', fxs: 'gfx/fx.png', boom: 'gfx/boom.png',
    enemies: 'gfx/enemies.png', decor: 'gfx/decor.png', font: 'gfx/font.png',
    tiles_park: 'gfx/tiles_park.png', tiles_cosmo: 'gfx/tiles_cosmo.png', tiles_ship: 'gfx/tiles_ship.png',
    park_sky: 'gfx/bg_park_sky.png', park_clouds: 'gfx/bg_park_clouds.png', park_far: 'gfx/bg_park_far.png',
    park_mid: 'gfx/bg_park_mid.png', park_near: 'gfx/bg_park_near.png',
    cosmo_sky: 'gfx/bg_cosmo_sky.png', cosmo_planets: 'gfx/bg_cosmo_planets.png',
    cosmo_far: 'gfx/bg_cosmo_far.png', cosmo_near: 'gfx/bg_cosmo_near.png',
    ship_space: 'gfx/bg_ship_space.png', ship_wall: 'gfx/bg_ship_wall.png',
    ship_lights0: 'gfx/bg_ship_lights0.png', ship_lights1: 'gfx/bg_ship_lights1.png', ship_mid: 'gfx/bg_ship_mid.png',
  };
  const POWER_ORDER = ['shield', 'triple', 'rapid', 'mega', 'superJump', 'magnet', 'heart', 'star',
    'turbo', 'freeze', 'ghost', 'ricochet', 'tornado', 'double', 'hover', 'seed'];
  const FONT_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZÉÈÀÇ+-x:!?.,'/*#() ";
  const FONT_IDX = {};
  for (let i = 0; i < FONT_CHARS.length; i++) FONT_IDX[FONT_CHARS[i]] = i;

  let pending = 0;
  function load() {
    for (const [k, f] of Object.entries(FILES)) {
      pending++;
      const im = new Image();
      im.onload = () => { G.img[k] = im; done(); };
      im.onerror = () => { G.failed[k] = true; done(); };
      im.src = BASE + f;
    }
  }
  function done() {
    pending--;
    if (pending > 0) return;
    try { prepare(); } catch (err) { console.warn('GFX prepare', err); }
    G.ready = !!(G.img.sousou && G.img.items && G.img.tiles_park);
    if (G.ready && G.img.font && document.body) document.body.classList.add('gfx-hud');
  }
  const has = (k) => !!G.img[k];

  // ---------------------------------------------------------------
  // Pré-calculs : silhouettes blanches (hit flash), cyan (gel), bas de calques
  // ---------------------------------------------------------------
  function mkCanvas(w, h) {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const x = c.getContext('2d');
    x.imageSmoothingEnabled = false;
    return [c, x];
  }
  function silhouette(im, color) {
    const [c, x] = mkCanvas(im.width, im.height);
    x.drawImage(im, 0, 0);
    x.globalCompositeOperation = 'source-in';
    x.fillStyle = color;
    x.fillRect(0, 0, c.width, c.height);
    return c;
  }
  const bottomColor = {};
  function sampleBottom(key) {
    const im = G.img[key];
    if (!im) return;
    try {
      const [c, x] = mkCanvas(im.width, 1);
      x.drawImage(im, 0, im.height - 1, im.width, 1, 0, 0, im.width, 1);
      const d = x.getImageData(0, 0, im.width, 1).data;
      let r = 0, g = 0, b = 0, n = 0;
      for (let i = 0; i < d.length; i += 4) if (d[i + 3] > 200) { r += d[i]; g += d[i + 1]; b += d[i + 2]; n++; }
      if (n) bottomColor[key] = 'rgb(' + Math.round(r / n) + ',' + Math.round(g / n) + ',' + Math.round(b / n) + ')';
    } catch (e) { /* file:// taint : on ignore */ }
  }
  function prepare() {
    if (G.img.enemies) {
      G.enemiesWhite = silhouette(G.img.enemies, '#ffffff');
      G.enemiesIce = silhouette(G.img.enemies, 'rgba(150,230,255,0.55)');
    }
    if (G.img.sousou) {
      G.sousouWhite = silhouette(G.img.sousou, '#ffffff');
      G.sousouGold = silhouette(G.img.sousou, 'rgba(255,220,90,0.45)');
    }
    ['park_far', 'park_mid', 'park_near', 'cosmo_far', 'cosmo_near', 'ship_mid'].forEach(sampleBottom);
    // halo doux pré-rendu (utilisé en mode additif, jamais recalculé)
    const [hc, hx] = mkCanvas(64, 64);
    const grd = hx.createRadialGradient(32, 32, 0, 32, 32, 32);
    grd.addColorStop(0, 'rgba(255,255,255,0.9)');
    grd.addColorStop(0.35, 'rgba(255,255,255,0.35)');
    grd.addColorStop(1, 'rgba(255,255,255,0)');
    hx.fillStyle = grd; hx.fillRect(0, 0, 64, 64);
    G.halo = hc;
    G.haloTint = {};
  }
  function tintedHalo(color) {
    let c = G.haloTint[color];
    if (c) return c;
    const [cc, x] = mkCanvas(64, 64);
    x.drawImage(G.halo, 0, 0);
    x.globalCompositeOperation = 'source-in';
    x.fillStyle = color; x.fillRect(0, 0, 64, 64);
    G.haloTint[color] = cc;
    return cc;
  }
  function glow(ctx, x, y, r, color, a) {
    if (lowFxMode || !G.halo) return;
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.globalAlpha = a;
    ctx.drawImage(tintedHalo(color), Math.round(x - r), Math.round(y - r), r * 2, r * 2);
    ctx.restore();
  }

  // hash déterministe (même décor à chaque partie)
  function hash(a, b, s) {
    let h = (a * 374761393 + b * 668265263 + (s || 0) * 2147483647) | 0;
    h = (h ^ (h >>> 13)) * 1274126177 | 0;
    return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
  }
  const themeOf = () => (levelDef && levelDef.theme) || 'park';
  const tilesImg = () => G.img['tiles_' + themeOf()] || G.img.tiles_park;

  // ---------------------------------------------------------------
  // POLICE PIXEL
  // ---------------------------------------------------------------
  const ACC = { 'é': 'É', 'è': 'È', 'ê': 'E', 'ë': 'E', 'à': 'À', 'â': 'A', 'ç': 'Ç', 'ô': 'O', 'î': 'I', 'ï': 'I', 'ù': 'U', 'û': 'U', '·': '-', '×': 'x', '…': '...' };
  function norm(s) {
    let out = '';
    for (const ch of String(s)) {
      let c = ACC[ch] || ch;
      if (c !== 'x') c = c.toUpperCase();
      if (c.length > 1) { out += c; continue; }
      if (FONT_IDX[c] !== undefined) out += c;
      else if (c === '★') out += '*';
    }
    return out.replace(/\s+/g, ' ').trim();
  }
  G.textWidth = (s, sc = 2) => norm(s).length * 6 * sc + sc;
  function text(ctx, s, x, y, sc = 2, color = 0, align = 'left') {
    const f = G.img.font;
    if (!f) return 0;
    const str = norm(s);
    const w = str.length * 6 * sc + sc;
    let cx = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
    cx = Math.round(cx); y = Math.round(y);
    for (const ch of str) {
      const i = FONT_IDX[ch];
      if (i !== undefined && ch !== ' ') ctx.drawImage(f, i * 7, color * 9, 7, 9, cx, y, 7 * sc, 9 * sc);
      cx += 6 * sc;
    }
    return w;
  }
  G.text = text;

  // ---------------------------------------------------------------
  // FOND : parallaxe multi-couches + portrait Sousou intégré
  // ---------------------------------------------------------------
  function wrapLayer(ctx, key, factor, y, drift) {
    const im = G.img[key];
    if (!im) return;
    const w = im.width;
    let ox = -((cameraX * factor + (drift || 0)) % w);
    if (ox > 0) ox -= w;
    ox = Math.floor(ox);
    y = Math.round(y);
    for (let x = ox; x < VW; x += w) ctx.drawImage(im, x, y);
    const bc = bottomColor[key];
    if (bc && y + im.height < VH) {
      ctx.fillStyle = bc;
      ctx.fillRect(0, y + im.height, VW, VH - y - im.height);
    }
  }
  function camRaise() {
    // 0 quand la caméra est tout en bas, jusqu'à ~140 quand elle monte
    const maxCamY = Math.max(0, LEVEL_H - VH);
    return Math.max(0, maxCamY - cameraY);
  }
  function sousouBackdrop(ctx) {
    if (typeof drawSousouMapBackground !== 'function') return;
    drawSousouMapBackground();
    G.skipSousouOnce = true; // l'appel suivant (dans draw()) est ignoré
  }
  function starsTwinkle(ctx, n, seed, fy) {
    for (let i = 0; i < n; i++) {
      const sx = Math.floor((hash(i, 1, seed) * 1400 - cameraX * 0.02) % 1400);
      const x = sx < 0 ? sx + 1400 : sx;
      if (x > VW) continue;
      const y = Math.floor(hash(i, 2, seed) * fy);
      const t = (frame * 0.05 + hash(i, 3, seed) * 6.28);
      const a = 0.35 + 0.65 * Math.abs(Math.sin(t));
      const big = hash(i, 4, seed) > 0.85;
      ctx.globalAlpha = a;
      ctx.fillStyle = hash(i, 5, seed) > 0.8 ? '#ffe9a8' : (hash(i, 6, seed) > 0.8 ? '#b9f6ff' : '#ffffff');
      ctx.fillRect(x, y, 2, 2);
      if (big && a > 0.8) {
        ctx.fillRect(x - 2, y, 6, 2);
        ctx.fillRect(x, y - 2, 2, 6);
      }
    }
    ctx.globalAlpha = 1;
  }
  G.drawBackground = function (ctx) {
    if (!G.ready) return false;
    const th = themeOf();
    const up = camRaise();
    ctx.imageSmoothingEnabled = false;
    if (th === 'park') {
      if (!has('park_sky')) return false;
      ctx.drawImage(G.img.park_sky, 0, 0);
      wrapLayer(ctx, 'park_clouds', 0.05, 18 + up * 0.05, frame * 0.12);
      sousouBackdrop(ctx);
      wrapLayer(ctx, 'park_far', 0.12, 222 + up * 0.18);
      wrapLayer(ctx, 'park_mid', 0.28, 212 + up * 0.35);
      wrapLayer(ctx, 'park_near', 0.5, 352 + up * 0.55);
    } else if (th === 'cosmo') {
      if (!has('cosmo_sky')) return false;
      ctx.drawImage(G.img.cosmo_sky, 0, 0);
      starsTwinkle(ctx, lowFxMode ? 25 : 60, 7, 420);
      wrapLayer(ctx, 'cosmo_planets', 0.03, up * 0.05, frame * 0.02);
      sousouBackdrop(ctx);
      wrapLayer(ctx, 'cosmo_far', 0.14, 250 + up * 0.2);
      wrapLayer(ctx, 'cosmo_near', 0.34, 292 + up * 0.45);
    } else {
      if (!has('ship_space')) return false;
      ctx.drawImage(G.img.ship_space, 0, 0);
      // étoiles en hyper-vitesse visibles par les hublots
      const n = lowFxMode ? 18 : 42;
      for (let i = 0; i < n; i++) {
        const sp = 2 + hash(i, 9, 3) * 7;
        const len = Math.round(sp * 3);
        let x = (VW + 40) - ((frame * sp + hash(i, 1, 3) * 2000) % (VW + 80));
        const y = Math.floor(hash(i, 2, 3) * VH);
        ctx.globalAlpha = 0.4 + hash(i, 4, 3) * 0.6;
        ctx.fillStyle = hash(i, 5, 3) > 0.75 ? '#c5f5ff' : '#ffffff';
        ctx.fillRect(Math.floor(x), y, len, 2);
      }
      ctx.globalAlpha = 1;
      wrapLayer(ctx, 'ship_wall', 0.3, 0);
      const lk = (frame >> 5) % 2 ? 'ship_lights1' : 'ship_lights0';
      wrapLayer(ctx, lk, 0.3, 0);
      sousouBackdrop(ctx);
      wrapLayer(ctx, 'ship_mid', 0.55, 244 + up * 0.5);
      // voile sombre : fait ressortir le pont de jeu devant la cloison
      ctx.fillStyle = 'rgba(6, 10, 22, 0.42)';
      ctx.fillRect(0, 0, VW, VH);
    }
    return true;
  };

  // ---------------------------------------------------------------
  // TUILES : pré-rendu par niveau (autotile + variantes + décor)
  // ---------------------------------------------------------------
  let cache = null, cacheKey = null;
  const CELL = 40;
  function tileAt(r, c) {
    if (r < 0) return '.';
    if (r >= ROWS) return LEVEL_ROWS[ROWS - 1][Math.max(0, Math.min(COLS - 1, c))];
    if (c < 0 || c >= COLS) return LEVEL_ROWS[r][Math.max(0, Math.min(COLS - 1, c))];
    return LEVEL_ROWS[r][c];
  }
  function blitTile(x, img, col, row, dx, dy) {
    x.drawImage(img, col * CELL, row * CELL, CELL, CELL, dx, dy, CELL, CELL);
  }
  function buildCache() {
    const th = themeOf();
    const img = tilesImg();
    const [c, x] = mkCanvas(COLS * T, ROWS * T);
    const deco = G.img.decor;
    const decoRow = th === 'park' ? 0 : th === 'cosmo' ? 1 : 2;
    for (let r = 0; r < ROWS; r++) {
      for (let col = 0; col < COLS; col++) {
        const ch = LEVEL_ROWS[r][col];
        const dx = col * T, dy = r * T;
        if (ch === '1') {
          let m = 0;
          if (tileAt(r - 1, col) !== '1') m |= 1;
          if (r + 1 < ROWS && tileAt(r + 1, col) !== '1') m |= 2;
          if (col > 0 && tileAt(r, col - 1) !== '1') m |= 4;
          if (col + 1 < COLS && tileAt(r, col + 1) !== '1') m |= 8;
          blitTile(x, img, m, hash(col, r, 11) < 0.5 ? 0 : 1, dx, dy);
          // décor posé sur le sol (pas sous le drapeau / tuyaux)
          if ((m & 1) && deco && tileAt(r - 1, col) === '.' && hash(col, r, 5) < (th === 'ship' ? 0.16 : 0.34)) {
            const k = Math.floor(hash(col, r, 6) * 8);
            const off = Math.floor(hash(col, r, 7) * 10) - 1;
            x.drawImage(deco, k * 32, decoRow * 32, 32, 32, dx + off, dy - 31, 32, 32);
          }
        } else if (ch === '2') {
          blitTile(x, img, 0, 2, dx, dy);
        } else if (ch === '4') {
          const L = tileAt(r, col - 1) === '4', R = tileAt(r, col + 1) === '4';
          const k = L && R ? 7 : L ? 8 : R ? 6 : 5;
          blitTile(x, img, k, 2, dx, dy);
        } else if (ch >= '5' && ch <= '8') {
          blitTile(x, img, 9 + (ch.charCodeAt(0) - 53), 2, dx, dy);
        } else if (ch === 'I') {
          const L = tileAt(r, col - 1) === 'I', R = tileAt(r, col + 1) === 'I';
          if (L && R) blitTile(x, img, 15, 2, dx, dy);
          else if (L) blitTile(x, img, 0, 3, dx, dy);
          else if (R) blitTile(x, img, 14, 2, dx, dy);
          else blitTile(x, img, 13, 2, dx, dy);
        }
      }
    }
    return c;
  }
  G.invalidateTiles = () => { cacheKey = null; };
  G.drawTiles = function (ctx) {
    if (!G.ready) return false;
    const key = (levelDef && levelDef.id) + '|' + themeOf() + '|' + LEVEL_ROWS.length + '|' + (LEVEL_ROWS[0] || '').length;
    if (!cache || cacheKey !== key || G._rowsRef !== LEVEL_ROWS) {
      cache = buildCache(); cacheKey = key; G._rowsRef = LEVEL_ROWS;
    }
    ctx.imageSmoothingEnabled = false;
    const sx = Math.max(0, Math.floor(cameraX) - 40), sy = Math.max(0, Math.floor(cameraY) - 40);
    const sw = Math.min(cache.width - sx, VW + 80), sh = Math.min(cache.height - sy, VH + 80);
    if (sw > 0 && sh > 0) ctx.drawImage(cache, sx, sy, sw, sh, sx, sy, sw, sh);
    // tuiles animées visibles
    const img = tilesImg();
    const c0 = Math.max(0, Math.floor(cameraX / T) - 1), c1 = Math.min(COLS - 1, Math.floor((cameraX + VW) / T) + 1);
    const r0 = Math.max(0, Math.floor(cameraY / T) - 1), r1 = Math.min(ROWS - 1, Math.floor((cameraY + VH) / T) + 1);
    for (let r = r0; r <= r1; r++) {
      const row = LEVEL_ROWS[r];
      for (let c = c0; c <= c1; c++) {
        const ch = row[c];
        const x = c * T, y = r * T;
        if (ch === '3') {
          const qb = questionBlocks.find(b => b.c === c && b.r === r);
          const by = y - (qb && qb.bounce ? Math.round(qb.bounce) : 0);
          if (qb && qb.used) blitTile(ctx, img, 4, 2, x, by);
          else {
            const f = [1, 1, 2, 3, 2, 1][(frame >> 3) % 6];
            blitTile(ctx, img, f, 2, x, by);
          }
        } else if (ch === 'X') {
          const f = ((frame >> 3) + c) % 4;
          const top = tileAt(r - 1, c) !== 'X';
          blitTile(ctx, img, top ? 3 + f : 7 + f, 3, x, y);
          if (top && !lowFxMode && ((frame + c * 13) % 90) < 2) {
            spawnParticle(x + 8 + hash(c, frame, 2) * 24, y + 4, 0, -1.5, 30, '#ffab40', 2);
          }
        } else if (ch === 'B') {
          const squish = Math.abs(player.x - (x + 20)) < 30 && Math.abs(player.y - y) < 6;
          blitTile(ctx, img, squish ? 2 : 1, 3, x, y);
        }
      }
    }
    return true;
  };

  // ---------------------------------------------------------------
  // OBJECTIF : drapeau pixel (parc) / portail (cosmo) / cockpit (vaisseau)
  // ---------------------------------------------------------------
  G.drawGoal = function (ctx) {
    if (!G.ready) return false;
    const x = Math.round(flag.x), y = Math.round(flag.y);
    const th = themeOf();
    if (th === 'park') {
      const top = y - flag.h;
      ctx.fillStyle = '#20301a'; ctx.fillRect(x + 7, top, 8, flag.h);
      ctx.fillStyle = '#e8eef0'; ctx.fillRect(x + 8, top, 5, flag.h);
      ctx.fillStyle = '#9aa8ad'; ctx.fillRect(x + 12, top, 2, flag.h);
      // boule dorée
      ctx.fillStyle = '#20301a'; ctx.fillRect(x + 3, top - 12, 16, 14);
      ctx.fillStyle = '#ffc93c'; ctx.fillRect(x + 4, top - 11, 14, 12);
      ctx.fillStyle = '#fff3b0'; ctx.fillRect(x + 6, top - 9, 4, 3);
      ctx.fillStyle = '#d9901a'; ctx.fillRect(x + 4, top - 2, 14, 3);
      // drapeau vert pistache qui ondule (bandes de 3px)
      const fy = Math.round(flagSliding ? Math.min(player.y - 40, y - 20) : top + 16 + Math.sin(frame * 0.08) * 3);
      for (let i = 0; i < 16; i++) {
        const w = 3, fx0 = x + 15 + i * w;
        const wave = Math.round(Math.sin(frame * 0.15 - i * 0.5) * 2);
        const h = Math.max(4, 34 - i * 2);
        const yy = fy + (34 - h) / 2 + wave;
        ctx.fillStyle = '#1e3a12'; ctx.fillRect(fx0, yy - 1, w, h + 2);
        ctx.fillStyle = i % 5 === 0 ? '#9ccc4f' : '#7cb342'; ctx.fillRect(fx0, yy, w, h);
        ctx.fillStyle = '#b5e06b'; ctx.fillRect(fx0, yy, w, 3);
      }
      const it = G.img.items;
      ctx.drawImage(it, 6 * 24, 3 * 24, 24, 24, x + 24, fy + 5, 24, 24);
      // socle
      ctx.fillStyle = '#20301a'; ctx.fillRect(x - 1, y - 9, 28, 10);
      ctx.fillStyle = '#90a4ae'; ctx.fillRect(x, y - 8, 26, 8);
      ctx.fillStyle = '#cfd8dc'; ctx.fillRect(x, y - 8, 26, 2);
      return true;
    }
    // portail (cosmo) / sas cockpit (vaisseau) : anneaux pixel animés
    const cx = x + 20, cy = y - 50;
    const ship = th === 'ship';
    const cols = ship ? ['#2e5a1c', '#8bc34a', '#dcedc8', '#ffeb3b'] : ['#3a1260', '#b36bff', '#f3c6ff', '#fff59d'];
    glow(ctx, cx, cy, 70, ship ? '#76ff03' : '#d500f9', 0.35 + Math.sin(frame * 0.1) * 0.1);
    for (let k = 0; k < 3; k++) {
      const rx = 24 - k * 6, ry = 44 - k * 10;
      const n = 28;
      for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2 + frame * (0.03 + k * 0.02) * (k % 2 ? -1 : 1);
        const px = Math.round(cx + Math.cos(a) * rx) - 2, py = Math.round(cy + Math.sin(a) * ry) - 2;
        ctx.fillStyle = cols[0]; ctx.fillRect(px - 1, py - 1, 6, 6);
        ctx.fillStyle = cols[1 + ((i + k) % 3 === 0 ? 1 : 0)]; ctx.fillRect(px, py, 4, 4);
      }
    }
    ctx.globalAlpha = 0.55 + Math.sin(frame * 0.2) * 0.2;
    ctx.fillStyle = cols[3];
    ctx.fillRect(cx - 6, cy - 16, 12, 32);
    ctx.fillRect(cx - 10, cy - 8, 20, 16);
    ctx.globalAlpha = 1;
    text(ctx, ship ? 'COCKPIT' : 'PORTAIL', cx, y - 110, 2, 1, 'center');
    return true;
  };

  // ---------------------------------------------------------------
  // PISTACHES (collectibles), POWER-UPS, MINES, MÉTÉORES
  // ---------------------------------------------------------------
  G.drawCoin = function (ctx, c) {
    if (!G.ready) return false;
    const y = c.pop ? c.y : c.baseY + Math.sin(c.bob) * 6;
    const f = Math.floor(frame * 0.18 + c.bob * 2) % 8;
    glow(ctx, c.x, y, 26, '#fff176', 0.42 + 0.12 * Math.sin(frame * 0.2 + c.bob));
    ctx.drawImage(G.img.items, f * 24, 0, 24, 24, Math.round(c.x - 12), Math.round(y - 12), 24, 24);
    const sp = (frame + Math.floor(c.bob * 37)) % 120;
    if (sp < 16 && G.img.fxs) {
      ctx.drawImage(G.img.fxs, (3 + Math.min(3, sp >> 2)) * 32, 96, 32, 32, Math.round(c.x - 6), Math.round(y - 26), 32, 32);
    }
    return true;
  };
  G.drawPowerup = function (ctx, p) {
    if (!G.ready) return false;
    const y = p.baseY + Math.sin(p.bob) * 6;
    const i = Math.max(0, POWER_ORDER.indexOf(p.type));
    const def = POWER_DEFS[p.type] || { color: '#fff' };
    glow(ctx, p.x, y, 30, def.color, 0.4 + Math.sin(frame * 0.15 + p.bob) * 0.15);
    // ombre
    ctx.fillStyle = 'rgba(0,0,0,0.25)';
    ctx.fillRect(Math.round(p.x - 9), Math.round(p.baseY + 16), 18, 3);
    ctx.drawImage(G.img.items, (i % 8) * 24, (5 + (i >> 3)) * 24, 24, 24, Math.round(p.x - 16), Math.round(y - 16), 32, 32);
    // étincelles orbitales (pixels)
    for (let k = 0; k < 3; k++) {
      const a = frame * 0.08 + k * 2.094 + p.bob;
      ctx.fillStyle = k === 0 ? '#ffffff' : def.color;
      ctx.fillRect(Math.round(p.x + Math.cos(a) * 22) - 1, Math.round(y + Math.sin(a) * 22) - 1, 3, 3);
    }
    return true;
  };
  G.drawMine = function (ctx, m) {
    if (!G.ready) return false;
    const armed = m.arm <= 0;
    const f = armed && (frame >> 3) % 2 ? 3 : 2;
    if (armed) glow(ctx, m.x, m.y - 8, 16, '#ff5252', 0.25 + ((frame >> 3) % 2) * 0.2);
    ctx.drawImage(G.img.items, f * 24, 3 * 24, 24, 24, Math.round(m.x - 12), Math.round(m.y - 20), 24, 24);
    return true;
  };
  G.drawMeteor = function (ctx, m) {
    if (!G.ready || !G.img.enemies) return false;
    // traînée de feu (carrés)
    const n = lowFxMode ? 4 : 8;
    for (let i = n; i >= 1; i--) {
      const s = Math.max(2, Math.round(m.r * 0.9 - i * 1.5));
      ctx.globalAlpha = 0.8 - i * 0.08;
      ctx.fillStyle = i < 3 ? '#fff59d' : i < 6 ? '#ffab40' : '#e65100';
      ctx.fillRect(Math.round(m.x - (m.vx || 0) * i * 2 - s / 2), Math.round(m.y - i * 7 - s / 2), s, s);
    }
    ctx.globalAlpha = 1;
    glow(ctx, m.x, m.y, 34, '#ff6d00', 0.45);
    ctx.save();
    ctx.translate(Math.round(m.x), Math.round(m.y));
    ctx.rotate(Math.round(m.rot / (Math.PI / 4)) * (Math.PI / 4));
    const row = themeOf() === 'cosmo' ? 4 : 1;
    ctx.drawImage(G.img.enemies, ((frame >> 3) % 4) * 48, row * 48, 48, 48, -24, -26, 48, 48);
    ctx.restore();
    return true;
  };

  // ---------------------------------------------------------------
  // PROJECTILES pistache : rotation, traînée, halo
  // ---------------------------------------------------------------
  const TRAIL = { lance: ['#f1ffd0', '#c5e86c', '#7cb342'], gun: ['#fffbd0', '#ffe066', '#cddc39'], grenade: ['#fff3c0', '#ffab40', '#8d6e63'] };
  G.drawBullet = function (ctx, b) {
    if (!G.ready) return false;
    const it = G.img.items;
    const mega = b.r > 18;
    const sc = mega ? 2 : 1;
    // historique pour la traînée
    const tr = b._tr || (b._tr = []);
    if (!paused) { tr.push(b.x, b.y); if (tr.length > (lowFxMode ? 8 : 16)) tr.splice(0, 2); }
    const cols = TRAIL[b.kind] || TRAIL.lance;
    const n = tr.length / 2;
    for (let i = 0; i < n - 1; i++) {
      const t = i / n;
      const s = Math.max(2, Math.round((b.kind === 'gun' ? 5 : 7) * t * sc));
      ctx.globalAlpha = 0.25 + t * 0.6;
      ctx.fillStyle = cols[t > 0.7 ? 0 : t > 0.35 ? 1 : 2];
      ctx.fillRect(Math.round(tr[i * 2] - s / 2), Math.round(tr[i * 2 + 1] - s / 2), s, s);
    }
    ctx.globalAlpha = 1;
    glow(ctx, b.x, b.y, 18 * sc, b.kind === 'grenade' ? '#ff9100' : (mega ? '#e040fb' : '#c6ff00'), 0.35);
    let col, row;
    if (b.kind === 'gun') {
      row = 3; col = (frame >> 2) % 2;
      const vert = Math.abs(b.vy) > Math.abs(b.vx);
      ctx.save();
      ctx.translate(Math.round(b.x), Math.round(b.y));
      if (vert) ctx.rotate(-Math.PI / 2);
      else if (b.vx < 0) ctx.scale(-1, 1);
      ctx.drawImage(it, col * 24, row * 24, 24, 24, -12 * sc, -12 * sc, 24 * sc, 24 * sc);
      ctx.restore();
      return true;
    }
    row = b.kind === 'grenade' ? 2 : 1;
    col = ((Math.floor(b.rot / (Math.PI / 4)) % 8) + 8) % 8;
    if (b.vx < 0) col = (8 - col) % 8;
    ctx.drawImage(it, col * 24, row * 24, 24, 24, Math.round(b.x - 12 * sc), Math.round(b.y - 12 * sc), 24 * sc, 24 * sc);
    if (b.kind === 'grenade' && (frame >> 2) % 2) {
      ctx.fillStyle = '#fff59d';
      ctx.fillRect(Math.round(b.x - 1), Math.round(b.y - 14 * sc), 3, 3);
    }
    return true;
  };

  // ---------------------------------------------------------------
  // EFFETS (sprites) : impacts, poofs, flash, explosions
  // ---------------------------------------------------------------
  const FXDEF = {
    poof: { img: 'fxs', row: 0, n: 6, sz: 32, spd: 4 },
    hit: { img: 'fxs', row: 1, n: 5, sz: 32, spd: 3 },
    hitOrange: { img: 'fxs', row: 2, n: 5, sz: 32, spd: 3 },
    spark: { img: 'fxs', row: 3, n: 4, col0: 3, sz: 32, spd: 4 },
    boom: { img: 'boom', row: 0, n: 7, sz: 64, spd: 4 },
  };
  G.spawnFx = function (kind, x, y, scale) {
    if (!G.ready) return;
    if (lowFxMode && G.fx.length > 16) return;
    if (G.fx.length > 48) G.fx.shift();
    G.fx.push({ kind, x, y, t: 0, s: scale || 1 });
  };
  G.drawFx = function (ctx) {
    if (!G.ready) return;
    for (let i = G.fx.length - 1; i >= 0; i--) {
      const f = G.fx[i];
      const d = FXDEF[f.kind];
      const im = d && G.img[d.img];
      const k = Math.floor(f.t / d.spd);
      if (!im || k >= d.n) { G.fx.splice(i, 1); continue; }
      const sz = d.sz * f.s;
      ctx.drawImage(im, ((d.col0 || 0) + k) * d.sz, d.row * d.sz, d.sz, d.sz,
        Math.round(f.x - sz / 2), Math.round(f.y - sz / 2), sz, sz);
      if (!paused) f.t++;
    }
  };

  // ---------------------------------------------------------------
  // ENNEMIS : sprites 48x48, 4 frames + écrasé, flash blanc, gel, poof
  // ---------------------------------------------------------------
  function enemyRow(e) {
    const th = themeOf();
    if (e.type === 'raisinBoss') return 9;
    if (e.species === 'raisin' || e.type === 'raisin') return e.flying ? 8 : 7;
    if (e.type === 'flyer' || e.flying) return 6;
    const base = th === 'cosmo' ? 3 : 0;
    return base + (e.type === 'angry' ? 1 : e.type === 'jumbo' ? 2 : 0);
  }
  G.drawEnemy = function (ctx, e) {
    if (!G.ready || !G.img.enemies) return false;
    const im = G.img.enemies;
    const row = enemyRow(e);
    const fly = row === 6 || row === 8;
    const big = e.type === 'jumbo' || e.type === 'raisinBoss';
    const flip = e.vx < 0;
    if (e.flat) {
      // écrasé (piétiné) ou pouf (tiré)
      const t = 30 - (e.flatTimer || 0);
      if (!e._poofed) { e._poofed = true; G.spawnFx('poof', e.x, e.y - (fly ? 18 : 16), big ? 1.6 : 1.25); }
      if (e.shot && t > 6) return true;
      ctx.globalAlpha = Math.min(1, (e.flatTimer || 0) / 10);
      const src = e.shot && (t >> 1) % 2 === 0 ? G.enemiesWhite : im;
      ctx.save();
      ctx.translate(Math.round(e.x), Math.round(fly ? e.y - 4 : e.y));
      if (flip) ctx.scale(-1, 1);
      ctx.drawImage(src, 4 * 48, row * 48, 48, 48, -24, -46, 48, 48);
      ctx.restore();
      ctx.globalAlpha = 1;
      return true;
    }
    const f = Math.floor(e.bob * 1.25) % 4;
    ctx.save();
    if (fly) ctx.translate(Math.round(e.x), Math.round(e.y - 18 + Math.sin(e.bob) * 2));
    else ctx.translate(Math.round(e.x), Math.round(e.y));
    if (flip) ctx.scale(-1, 1);
    const oy = fly ? -25 : -46;
    // ombre au sol
    if (!fly) { ctx.fillStyle = 'rgba(0,0,0,0.22)'; ctx.fillRect(-12, -2, 24, 3); }
    if (big) glow(ctx, 0, oy + 26, 30, e.species === 'raisin' ? '#ff1744' : '#ff5722', 0.18);
    ctx.drawImage(im, f * 48, row * 48, 48, 48, -24, oy, 48, 48);
    if (buffs.freeze > 0 && G.enemiesIce) ctx.drawImage(G.enemiesIce, f * 48, row * 48, 48, 48, -24, oy, 48, 48);
    if (e.hitT > 0) {
      ctx.globalAlpha = Math.min(1, e.hitT / 4);
      ctx.drawImage(G.enemiesWhite, f * 48, row * 48, 48, 48, -24, oy, 48, 48);
      ctx.globalAlpha = 1;
      if (!paused) e.hitT--;
    }
    ctx.restore();
    // barre de vie pixel pour les costauds
    const maxHp = big ? 3 : e.type === 'angry' ? 2 : 1;
    if (maxHp > 1 && e.hp < maxHp && e.hp > 0) {
      const bx = Math.round(e.x - 12), by = Math.round((fly ? e.y - 44 : e.y - e.h - 12));
      ctx.fillStyle = '#1a1020'; ctx.fillRect(bx - 1, by - 1, 26, 6);
      ctx.fillStyle = '#5a2330'; ctx.fillRect(bx, by, 24, 4);
      ctx.fillStyle = '#ff5252'; ctx.fillRect(bx, by, Math.round(24 * e.hp / maxHp), 4);
      ctx.fillStyle = '#ff9e9e'; ctx.fillRect(bx, by, Math.round(24 * e.hp / maxHp), 1);
    }
    return true;
  };

  // ---------------------------------------------------------------
  // SOUSOU : machine à états du sprite officiel
  // ---------------------------------------------------------------
  const PS = { runPhase: 0, idleT: 0, blinkT: 0, nextBlink: 150, lastX: 0, dustT: 0, wasGround: true };
  function pickFrame() {
    const p = player;
    const moving = Math.abs(p.vx) > 0.6;
    if ((p.hurtT || 0) > 0) return 'hurt';
    if (!p.onGround) {
      if ((p.shootT || 0) > 0) return (p.shootT > 6 ? 'shoot_1' : 'shoot_0');
      return p.vy < 0 ? 'jump' : 'fall';
    }
    if (p.crouching) return 'jump';
    if ((p.shootT || 0) > 0) return p.shootT > 6 ? 'shoot_1' : 'shoot_0';
    if (moving) {
      return SP_ANIMS.run[Math.floor(PS.runPhase) % 6];
    }
    if (PS.blinkT > 0) return 'blink';
    return SP_ANIMS.idle[Math.floor(PS.idleT / 12) % 4];
  }
  function stepPlayerAnim() {
    const p = player;
    if (paused) return;
    if (p.shootT > 0) p.shootT--;
    if (p.hurtT > 0) p.hurtT--;
    if (p.onGround && Math.abs(p.vx) > 0.6) PS.runPhase += 0.12 + Math.abs(p.vx) * 0.055;
    else PS.runPhase = 0;
    PS.idleT++;
    if (PS.blinkT > 0) PS.blinkT--;
    else if (--PS.nextBlink <= 0) { PS.blinkT = 7; PS.nextBlink = 90 + Math.floor(Math.random() * 200); }
    // poussière de course / atterrissage
    if (!lowFxMode && p.onGround && Math.abs(p.vx) > 3 && ++PS.dustT % 8 === 0) {
      spawnParticle(p.x - p.facing * 10, p.y - 2, -p.facing * 0.6, -0.6, 16, themeOf() === 'park' ? '#d7c7a0' : '#cfd8dc', 2);
    }
    if (p.onGround && !PS.wasGround) {
      G.spawnFx('poof', p.x, p.y - 6, 0.6);
    }
    PS.wasGround = p.onGround;
  }
  G.drawPlayer = function (ctx) {
    if (!G.ready) return false;
    const p = player;
    stepPlayerAnim();
    if (typeof invuln !== 'undefined' && invuln > 0 && !(p.hurtT > 0) && Math.floor(frame / 4) % 2 === 0 && buffs.star <= 0) {
      ctx.globalAlpha = 0.35;
    }
    const name = pickFrame();
    const fr = SP_FRAMES[name];
    const flip = p.facing < 0;
    // squash/stretch subtil (50% de l'effet d'origine), tailles entières
    const sq = typeof playerSquash === 'number' ? playerSquash : 1;
    const st = typeof playerStretch === 'number' ? playerStretch : 1;
    let sx = 1, sy = 1;
    if (st > 1) { sy = 1 + (st - 1) * 0.5; sx = 1 - (st - 1) * 0.3; }
    if (sq > 1) { sx = 1 + (sq - 1) * 0.5; sy = 1 - (sq - 1) * 0.35; }
    const dw = Math.round(SP.w * sx), dh = Math.round(SP.h * sy);
    const ax = Math.round(SP.ax * sx);
    // ombre
    if (p.onGround) { ctx.save(); ctx.globalAlpha *= 0.28; ctx.fillStyle = '#000'; ctx.fillRect(Math.round(p.x - 13), Math.round(p.y - 2), 26, 3); ctx.fillRect(Math.round(p.x - 9), Math.round(p.y - 3), 18, 5); ctx.restore(); }
    if (themeOf() !== 'park') glow(ctx, p.x, p.y - 26, 40, '#fff8e1', 0.16);
    ctx.save();
    ctx.translate(Math.round(p.x), Math.round(p.y));
    if (flip) ctx.scale(-1, 1);
    const ghost = buffs.ghost > 0;
    if (ghost) ctx.globalAlpha *= 0.6;
    ctx.drawImage(G.img.sousou, fr[0], fr[1], SP.w, SP.h, -ax, -dh, dw, dh);
    if (buffs.star > 0 && G.sousouGold && (frame >> 2) % 2) {
      ctx.drawImage(G.sousouGold, fr[0], fr[1], SP.w, SP.h, -ax, -dh, dw, dh);
    }
    if ((p.hurtT || 0) > 30 && G.sousouWhite) {
      ctx.drawImage(G.sousouWhite, fr[0], fr[1], SP.w, SP.h, -ax, -dh, dw, dh);
    }
    // flash de bouche du blaster pistache (canon à droite du sprite ~ x=+24, y=-31)
    if ((p.shootT || 0) > 8 && G.img.fxs && !p.aimUp) {
      const k = Math.min(2, 12 - p.shootT);
      ctx.drawImage(G.img.fxs, k * 32, 96, 32, 32, 20, -31 - 16 + (p.crouching ? 12 : 0), 32, 32);
    }
    ctx.restore();
    if ((p.shootT || 0) > 8 && p.aimUp && G.img.fxs) {
      ctx.save();
      ctx.translate(Math.round(p.x), Math.round(p.y - p.h + 6));
      ctx.rotate(-Math.PI / 2);
      ctx.drawImage(G.img.fxs, Math.min(2, 12 - p.shootT) * 32, 96, 32, 32, -6, -16, 32, 32);
      ctx.restore();
    }
    ctx.globalAlpha = 1;
    return true;
  };
  G.onShoot = function () { player.shootT = 12; };
  G.onHurt = function () { player.hurtT = 40; };

  // ---------------------------------------------------------------
  // PARTICULES carrées (pixel) — remplace les cercles
  // ---------------------------------------------------------------
  G.drawParticles = function (ctx) {
    if (!G.ready) return false;
    for (const p of particles) {
      if (!inViewXY(p.x, p.y, 40)) continue;
      ctx.globalAlpha = Math.min(1, p.life / 15);
      ctx.fillStyle = p.color;
      const s = p.size > 4 ? 4 : (p.size > 2.6 ? 3 : 2);
      ctx.fillRect(Math.round(p.x - s / 2), Math.round(p.y - s / 2), s, s);
    }
    ctx.globalAlpha = 1;
    return true;
  };
  G.drawFloat = function (ctx, f) {
    if (!G.ready || !G.img.font) return false;
    const s = norm(f.text);
    if (!s) return false;
    ctx.globalAlpha = Math.min(1, f.life / 20);
    const col = /OUCH|-1|💔/.test(f.text) ? 3 : /VIE|\+1|BLOQU/.test(f.text) ? 2 : 1;
    text(ctx, s, f.x, f.y - 14, 2, col, 'center');
    ctx.globalAlpha = 1;
    return true;
  };

  // ---------------------------------------------------------------
  // HUD PIXEL (canvas) : coeurs, pistaches, score, temps, arme
  // ---------------------------------------------------------------
  function panel(ctx, x, y, w, h) {
    x = Math.round(x); y = Math.round(y);
    ctx.fillStyle = 'rgba(12, 18, 10, 0.72)';
    ctx.fillRect(x + 2, y, w - 4, h);
    ctx.fillRect(x, y + 2, w, h - 4);
    ctx.fillStyle = 'rgba(255,255,255,0.16)';
    ctx.fillRect(x + 2, y + 1, w - 4, 2);
    ctx.fillStyle = 'rgba(0,0,0,0.35)';
    ctx.fillRect(x + 2, y + h - 2, w - 4, 2);
  }
  function icon(ctx, col, row, x, y, s) {
    ctx.drawImage(G.img.items, col * 24, row * 24, 24, 24, Math.round(x), Math.round(y), 24 * (s || 1), 24 * (s || 1));
  }
  let hudPulse = { p: 0, s: 0, lastP: -1, lastS: -1 };
  G.drawHud = function (ctx) {
    if (!G.ready || !G.img.font || !running) return false;
    ctx.save();
    ctx.imageSmoothingEnabled = false;
    if (pistaches !== hudPulse.lastP) { if (hudPulse.lastP >= 0) hudPulse.p = 10; hudPulse.lastP = pistaches; }
    if (hudPulse.p > 0) hudPulse.p--;
    let x = 118;
    const y = 10, h = 34;
    // coeurs
    const hearts = Math.max(0, lives);
    const showN = hearts <= 5 ? hearts : 1;
    const hw = 10 + showN * 22 + (hearts > 5 ? G.textWidth('x' + hearts) + 4 : 0) + (hearts === 0 ? 22 : 0);
    panel(ctx, x, y, hw, h);
    if (hearts === 0) icon(ctx, 5, 3, x + 5, y + 5);
    for (let i = 0; i < showN; i++) {
      const bob = (hearts <= 2 && (frame >> 3) % 2 && i === showN - 1) ? -2 : 0;
      icon(ctx, 4, 3, x + 5 + i * 22, y + 5 + bob);
    }
    if (hearts > 5) text(ctx, 'x' + hearts, x + 32, y + 8, 2, 0);
    x += hw + 8;
    // pistaches
    const pw = 36 + G.textWidth(String(pistaches));
    panel(ctx, x, y, pw, h);
    icon(ctx, 6, 3, x + 4, y + 5 - (hudPulse.p > 5 ? 2 : 0));
    text(ctx, String(pistaches), x + 30, y + 8, 2, hudPulse.p > 0 ? 1 : 2);
    x += pw + 8;
    // score
    const sw = 36 + G.textWidth(String(score));
    panel(ctx, x, y, sw, h);
    icon(ctx, 7, 3, x + 4, y + 5);
    text(ctx, String(score), x + 30, y + 8, 2, 1);
    x += sw + 8;
    // temps
    const tl = Math.max(0, Math.ceil(timeLeft));
    const tw = 36 + G.textWidth(String(tl));
    panel(ctx, x, y, tw, h);
    icon(ctx, 3, 4, x + 4, y + 5);
    text(ctx, String(tl), x + 30, y + 8, 2, tl <= 60 && (frame >> 4) % 2 ? 3 : 0);
    x += tw + 8;
    // arme
    const w = WEAPONS[weaponIndex];
    const wname = w.id === 'lance' ? 'LANCE' : w.id === 'gun' ? 'GUN' : 'GRENADE';
    const ww = 36 + G.textWidth(wname);
    if (x + ww < VW - 110) {
      panel(ctx, x, y, ww, h);
      icon(ctx, weaponIndex, 4, x + 4, y + 5);
      text(ctx, wname, x + 30, y + 8, 2, 2);
      x += ww + 8;
    }
    // monde (en bas à gauche) + buffs
    const lbl = levelDef.code + ' ' + levelDef.title;
    ctx.globalAlpha = 0.85;
    icon(ctx, 7, 3, 6, VH - 30);
    text(ctx, lbl, 30, VH - 24, 2, 1);
    ctx.globalAlpha = 1;
    let bx = 12;
    const by = VH - 62;
    for (const [k, v] of Object.entries(buffs)) {
      if (v <= 0 || !POWER_DEFS[k]) continue;
      const i = POWER_ORDER.indexOf(k);
      const secs = String(Math.ceil(v / 60));
      const bw = 30 + G.textWidth(secs);
      panel(ctx, bx, by, bw, 30);
      if (i >= 0) icon(ctx, i % 8, 5 + (i >> 3), bx + 3, by + 3);
      if (v < 90 && (frame >> 3) % 2) ctx.globalAlpha = 0.4;
      text(ctx, secs, bx + 28, by + 7, 2, 0);
      ctx.globalAlpha = 1;
      bx += bw + 6;
    }
    if (player.aimUp) text(ctx, 'TIR HAUT', VW - 12, VH - 24, 2, 1, 'right');
    ctx.restore();
    return true;
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
