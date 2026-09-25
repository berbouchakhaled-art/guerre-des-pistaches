/* Menu principal animé (pixel art) — La guerre des pistaches
 * Dessine dans #menuFx : décor parallaxe des 3 mondes (fondu enchaîné), pluie de
 * pistaches qui tournent, rayons « héros », logo arcade qui ondule + reflet,
 * Sousou EN PIED (sprite HD, échelle entière) : respire, cligne des yeux, tire une
 * pistache ou saute de temps en temps. Aperçus animés des mondes dans les cartes.
 * Tout est à l'échelle entière (image-rendering: pixelated) → net sur téléphone.
 */
(function () {
  'use strict';
  const scr = document.getElementById('startScreen');
  const cv = document.getElementById('menuFx');
  if (!scr || !cv) return;
  const ctx = cv.getContext('2d');
  const MENU = window.MENU = { active: false };
  const LOGO_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZÉ!*-'";
  const HDC = { w: 144, h: 192, cx: 66, top: 39 };           // cellule sprite HD (x3), centre du corps
  const FR = {
    idle: [[0, 0], [1, 0], [2, 0], [3, 0]], jump: [4, 1], fall: [5, 1],
    shoot0: [0, 2], shoot1: [1, 2], blink: [2, 2], run: [[4, 0], [5, 0], [0, 1], [1, 1], [2, 1], [3, 1]],
  };
  const THEMES = ['park', 'cosmo', 'ship'];
  const reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  let W = 0, H = 0, bs = 1, px = 2;
  let logoR = null, stageR = null;
  let last = 0, T = 0, raf = 0;
  const img = (k) => (window.GFX && GFX.img && GFX.img[k]) || null;

  // ---------------------------------------------------------------- taille
  function resize() {
    const dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 3));
    // pixel de rendu = m pixels écran, m ENTIER (2 sur dpr 3) → pixels d'art carrés et réguliers ;
    // plafond de pixels de rendu (grandes tablettes) pour garder 60 i/s, toujours en m entier
    const area = window.innerWidth * window.innerHeight;
    let m = dpr >= 2.5 ? 2 : 1;
    while (area * (dpr / m) * (dpr / m) > 1.5e6 && dpr / (m + 1) >= 0.75) m++;
    bs = dpr / m;
    const cw = Math.max(1, Math.round(window.innerWidth * bs));
    const ch = Math.max(1, Math.round(window.innerHeight * bs));
    if (cv.width !== cw || cv.height !== ch) { cv.width = cw; cv.height = ch; }
    // 1 px de rendu = m px écran exactement (pas d'étirement CSS fractionnaire)
    cv.style.setProperty('width', cw / bs + 'px', 'important'); cv.style.setProperty('height', ch / bs + 'px', 'important');
    W = cw; H = ch;
    ctx.imageSmoothingEnabled = false;
    px = Math.max(1, Math.round(Math.min(W, H) / 300));
    const rect = (sel) => {
      const el = scr.querySelector(sel);
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { x: r.left * bs, y: r.top * bs, w: r.width * bs, h: r.height * bs };
    };
    logoR = rect('.m2-logo');
    stageR = rect('.m2-stage');
    vign = null;
    drawPlayLabel();
  }

  // ---------------------------------------------------------------- décor
  const SCENES = {
    park: { sky: 'park_sky', layers: [['park_clouds', 18, 5, true], ['park_far', 222, 9], ['park_mid', 212, 18], ['park_near', 352, 34]] },
    cosmo: { sky: 'cosmo_sky', stars: true, layers: [['cosmo_planets', 0, 3, true], ['cosmo_far', 250, 10], ['cosmo_near', 292, 26]] },
    ship: { sky: 'ship_space', warp: true, layers: [['ship_wall', 0, 14], ['ship_mid', 244, 30]] },
  };
  function sceneScale() { return Math.max(1, Math.round(H / 560)); }
  function drawScene(th, t, alpha) {
    const sc = SCENES[th];
    const sky = img(sc.sky);
    if (!sky) return false;
    const s = sceneScale();
    const oy = Math.round(H - 505 * s); // bas du décor (buissons) collé au bas de l'écran
    ctx.globalAlpha = alpha;
    const sw = Math.max(W, 960 * s);
    ctx.drawImage(sky, 0, 0, sky.width, sky.height, 0, oy, sw, sky.height * s);
    if (oy > 0) ctx.drawImage(sky, 0, 0, sky.width, 1, 0, 0, sw, oy + 1);
    if (sc.stars) {
      for (let i = 0; i < 70; i++) {
        const x = (i * 131 % 997) / 997 * W, y = (i * 71 % 613) / 613 * H * 0.7;
        const tw = ((i * 7 + Math.floor(t * 6)) % 9) < 2;
        ctx.fillStyle = tw ? '#ffffff' : (i % 5 ? '#b3e5fc' : '#fff59d');
        const z = (tw ? 2 : 1) * px;
        ctx.fillRect(Math.round(x), Math.round(y), z, z);
      }
    }
    if (sc.warp) {
      ctx.fillStyle = '#e1f5fe';
      for (let i = 0; i < 40; i++) {
        const sp = 0.4 + (i % 5) * 0.25;
        const x = W - ((t * 380 * sp * px + i * 97 * px) % (W + 200 * px));
        const y = ((i * 53) % 97) / 97 * H;
        ctx.globalAlpha = alpha * (0.35 + (i % 3) * 0.2);
        ctx.fillRect(Math.round(x), Math.round(y), (10 + (i % 4) * 8) * px, px);
      }
      ctx.globalAlpha = alpha;
    }
    for (const [key, y, speed, drift] of sc.layers) {
      const im = img(key);
      if (!im) continue;
      const w = im.width * s;
      let ox = -((t * speed * s * (drift ? 1 : 1.6)) % w);
      ox = Math.floor(ox);
      const yy = Math.round(oy + y * s);
      for (let x = ox; x < W; x += w) ctx.drawImage(im, 0, 0, im.width, im.height, x, yy, w, im.height * s);
    }
    if (th === 'ship') { ctx.fillStyle = 'rgba(4,10,8,0.35)'; ctx.fillRect(0, 0, W, H); }
    ctx.globalAlpha = 1;
    return true;
  }

  // ---------------------------------------------------------------- pistaches
  const nuts = [];
  function initNuts() {
    nuts.length = 0;
    for (let i = 0; i < 22; i++) nuts.push(newNut(true, i));
  }
  function newNut(anyY, i) {
    const r = Math.random();
    return {
      x: Math.random() * W, y: anyY ? Math.random() * H : -40 * px,
      v: (26 + Math.random() * 40) * px, ph: Math.random() * 6.28, f: Math.random() * 8,
      fs: 8 + Math.random() * 8, z: r < 0.6 ? 1 : 2, front: (i || 0) % 7 === 0,
    };
  }
  function drawNuts(dt, front) {
    const it = img('items');
    if (!it) return;
    for (let i = 0; i < nuts.length; i++) {
      const n = nuts[i];
      if (n.front !== front) continue;
      n.y += n.v * n.z * 0.6 * dt;
      n.f += n.fs * dt;
      if (n.y > H + 30 * px) nuts[i] = newNut(false, i);
      const z = n.z === 2 ? px : Math.max(1, px - 1);
      const x = Math.round(n.x + Math.sin(T * 1.3 + n.ph) * 10 * px);
      ctx.globalAlpha = n.z === 1 ? 0.55 : 0.95;
      ctx.drawImage(it, (Math.floor(n.f) % 8) * 24, 0, 24, 24, x, Math.round(n.y), 24 * z, 24 * z);
    }
    ctx.globalAlpha = 1;
  }

  // ---------------------------------------------------------------- logo
  const logoOff = document.createElement('canvas');
  const lctx = logoOff.getContext('2d');
  function wordW(str) {
    let w = 0;
    for (const ch of str) w += ch === ' ' ? 8 : 13;
    return w + 2;
  }
  function drawWord(c, str, x, y, style, wave, t) {
    const f = img('logoFont');
    let cx = x;
    let i = 0;
    for (const ch of str) {
      if (ch === ' ') { cx += 8; i++; continue; }
      const k = LOGO_CHARS.indexOf(ch);
      const dy = wave ? Math.round(Math.sin(t * 4 - i * 0.6) * 2) : 0;
      if (k >= 0) c.drawImage(f, k * 15, style * 21, 15, 21, cx, y + dy, 15, 21);
      cx += 13; i++;
    }
  }
  function drawLogo(t) {
    if (!logoR || !img('logoFont')) return false;
    const L1 = 'LA GUERRE DES', L2 = 'PISTACHES';
    const w1 = wordW(L1), w2 = wordW(L2);
    // échelles entières : ligne 2 plus grosse
    let b = Math.max(1, Math.floor(logoR.w * 0.98 / w2));
    let a = Math.max(1, Math.round(b * 0.55));
    const hTot = (bb, aa) => 26 * aa + 26 * bb + 12 * aa;
    while (b > 1 && (hTot(b, a) > logoR.h || w1 * a > logoR.w)) { b--; a = Math.max(1, Math.round(b * 0.55)); }
    const bounce = reduce ? 0 : Math.round(Math.abs(Math.sin(t * 2.2)) * -2) * a;
    let y = Math.round(logoR.y + (logoR.h - hTot(b, a)) / 2);
    const cx = logoR.x + logoR.w / 2;
    // ligne 1 (dorée)
    logoOff.width = w1; logoOff.height = 26;
    lctx.imageSmoothingEnabled = false;
    drawWord(lctx, L1, 0, 2, 0, false, t);
    ctx.drawImage(logoOff, Math.round(cx - w1 * a / 2), y + bounce, w1 * a, 26 * a);
    y += 24 * a;
    // ligne 2 (pistache) : lettres qui ondulent + reflet qui balaie
    logoOff.width = w2 + 2; logoOff.height = 28;
    lctx.imageSmoothingEnabled = false;
    drawWord(lctx, L2, 0, 3, 1, !reduce, t);
    const sp = (t % 3.2) / 3.2;
    if (sp < 0.45) {
      const sx = -20 + sp / 0.45 * (w2 + 40);
      lctx.globalCompositeOperation = 'source-atop';
      lctx.fillStyle = 'rgba(255,255,240,0.75)';
      lctx.beginPath();
      lctx.moveTo(sx, 0); lctx.lineTo(sx + 6, 0); lctx.lineTo(sx - 4, 28); lctx.lineTo(sx - 10, 28);
      lctx.fill();
      lctx.globalCompositeOperation = 'source-over';
    }
    ctx.drawImage(logoOff, Math.round(cx - (w2 + 2) * b / 2), y, (w2 + 2) * b, 28 * b);
    y += 27 * b;
    // ★ SOUSOU ★
    if (window.GFX && GFX.text) GFX.text(ctx, '* SOUSOU *', Math.round(cx), y, Math.max(1, a), 1, 'center');
    return true;
  }

  // ---------------------------------------------------------------- JOUER (police arcade)
  function drawPlayLabel() {
    const btn = document.getElementById('startBtn');
    const f = img('logoFont');
    if (!btn || !f) return;
    let c = btn.querySelector('canvas.p-lbl');
    if (!c) {
      c = document.createElement('canvas');
      c.className = 'p-lbl';
      c.setAttribute('aria-hidden', 'true');
      btn.insertBefore(c, btn.firstChild);
    }
    const word = 'JOUER !';
    const w = wordW(word) + 18;
    c.width = w; c.height = 24;
    const x = c.getContext('2d');
    x.imageSmoothingEnabled = false;
    // triangle « play »
    x.fillStyle = '#2e1a0c';
    for (let i = 0; i < 9; i++) x.fillRect(1, 3 + i, Math.min(i, 8 - i) + 2 + 5, 1);
    x.fillStyle = '#fff3c4';
    for (let i = 1; i < 8; i++) x.fillRect(2, 3 + i, Math.min(i, 8 - i) + 4, 1);
    drawWord(x, word, 16, 1, 1, false, 0);
    c.style.height = (24 * 2) + 'px';
    c.style.width = (w * 2) + 'px';
    btn.classList.add('lbl-on');
  }

  // ---------------------------------------------------------------- Sousou
  const S = { mode: 'idle', t: 0, next: 2.2, blink: 1.6, k: 0, y: 0, shots: 0, flash: 0 };
  const shots = [], dusts = [];
  MENU.pose = (m) => { S.mode = m; S.t = 0; S.shots = 0; S.next = 9; };
  function stepSousou(dt) {
    S.t += dt; S.next -= dt; S.blink -= dt;
    if (S.blink < -0.13) S.blink = 2 + Math.random() * 2.5;
    if (S.mode === 'idle' && S.next <= 0 && !reduce) {
      S.mode = S.k++ % 2 === 0 ? 'shoot' : 'jump';
      S.t = 0; S.shots = 0;
    }
    if (S.mode === 'shoot') {
      if ((S.shots === 0 && S.t > 0.25) || (S.shots === 1 && S.t > 0.7)) { S.shots++; S.flash = 0.12; fire(); }
      if (S.t > 1.15) { S.mode = 'idle'; S.next = 3 + Math.random() * 2; }
    } else if (S.mode === 'jump') {
      const p = S.t / 0.8;
      S.y = p < 1 ? Math.sin(Math.PI * p) * 34 : 0;
      if (p >= 1) { S.mode = 'idle'; S.next = 3 + Math.random() * 2; S.y = 0; dusts.push({ t: 0 }); }
    }
    if (S.flash > 0) S.flash -= dt;
  }
  let lastGeo = null;
  function fire() {
    if (!lastGeo) return;
    shots.push({ x: lastGeo.mx, y: lastGeo.my, f: 0 });
  }
  function drawStage(dt, th) {
    const sp = img('sousouHD');
    if (!stageR || !sp) return;
    const tiles = img('tiles_' + th) || img('tiles_park');
    // échelle ENTIÈRE uniquement : Sousou (153 px d'art) remplit ~80 % de la scène,
    // chaque pixel d'art = s x s pixels de rendu → jamais déformé
    const fit = (stageR.h * 0.94 - 20) / 160;
    let s = Math.max(1, Math.floor(fit));
    while (s > 1 && 76 * s > stageR.w * 0.95) s--;
    const cx = Math.round(stageR.x + stageR.w / 2);
    const platH = 22 * s;
    const groundY = Math.round(stageR.y + stageR.h - platH * 1.25);
    // rayons « héros » derrière Sousou
    if (!reduce) {
      ctx.save();
      ctx.translate(cx, groundY - 70 * s);
      ctx.rotate(T * 0.25);
      ctx.globalAlpha = 0.13;
      ctx.fillStyle = th === 'park' ? '#fff59d' : '#c5e1a5';
      const R = Math.max(stageR.w, stageR.h) * 0.75;
      for (let i = 0; i < 12; i++) {
        const a0 = i / 12 * Math.PI * 2, a1 = a0 + Math.PI / 12;
        ctx.beginPath(); ctx.moveTo(0, 0);
        ctx.lineTo(Math.cos(a0) * R, Math.sin(a0) * R); ctx.lineTo(Math.cos(a1) * R, Math.sin(a1) * R);
        ctx.fill();
      }
      ctx.restore();
    }
    // plateforme flottante (tuiles du monde courant)
    if (tiles) {
      const pw = 160 * s;
      const bobP = Math.round(Math.sin(T * 1.5) * 1.5) * s;
      const lx = Math.round(cx - pw / 2);
      // plateforme L · M · M · R (rangée 2 de l'atlas de tuiles 40 px)
      ctx.drawImage(tiles, 240, 80, 40, 22, lx, groundY + bobP, 40 * s, platH);
      ctx.drawImage(tiles, 280, 80, 40, 22, lx + 40 * s, groundY + bobP, 40 * s, platH);
      ctx.drawImage(tiles, 280, 80, 40, 22, lx + 80 * s, groundY + bobP, 40 * s, platH);
      ctx.drawImage(tiles, 320, 80, 40, 22, lx + 120 * s, groundY + bobP, 40 * s, platH);
    }
    const bob = Math.round(Math.sin(T * 1.5) * 1.5) * s;
    const feet = groundY + bob + 3 * s;
    // ombre
    const sh = Math.max(0.3, 1 - S.y / 60);
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.fillRect(Math.round(cx - 24 * s * sh), feet - 2 * s, Math.round(48 * s * sh), 3 * s);
    // image
    let fr;
    if (S.mode === 'shoot') fr = S.flash > 0 ? FR.shoot1 : FR.shoot0;
    else if (S.mode === 'jump') fr = S.t < 0.4 ? FR.jump : FR.fall;
    else fr = S.blink < 0 ? FR.blink : FR.idle[Math.floor(T * 3.5) % 4];
    const x0 = Math.round(cx - HDC.cx * s);
    const y0 = Math.round(feet - HDC.h * s - Math.round(S.y) * s);
    ctx.drawImage(sp, fr[0] * HDC.w, fr[1] * HDC.h, HDC.w, HDC.h, x0, y0, HDC.w * s, HDC.h * s);
    lastGeo = { mx: x0 + 138 * s, my: y0 + 110 * s, s };
    // tirs de pistaches
    const it = img('items');
    for (let i = shots.length - 1; i >= 0; i--) {
      const b = shots[i];
      b.x += 520 * s * dt; b.f += 18 * dt;
      if (b.x > W + 40) { shots.splice(i, 1); continue; }
      if (it) ctx.drawImage(it, (Math.floor(b.f) % 8) * 24, 0, 24, 24, Math.round(b.x), Math.round(b.y - 12 * s), 24 * s, 24 * s);
    }
    const fx = img('fxs');
    if (fx && S.flash > 0) ctx.drawImage(fx, 32, 96, 32, 32, lastGeo.mx - 8 * s, lastGeo.my - 16 * s, 32 * s, 32 * s);
    for (let i = dusts.length - 1; i >= 0; i--) {
      const d = dusts[i];
      d.t += dt;
      const k = Math.floor(d.t * 16);
      if (k >= 6) { dusts.splice(i, 1); continue; }
      if (fx) ctx.drawImage(fx, k * 32, 0, 32, 32, cx - 32 * s, feet - 22 * s, 64 * s, 32 * s);
    }
  }

  // ---------------------------------------------------------------- aperçus des mondes
  const previews = Array.from(scr.querySelectorAll('canvas.wprev'));
  const PREV = {
    park: { label: '1 PARC', en: [0, 0], tiles: 'tiles_park', col: 0 },
    cosmo: { label: '2 COSMOS', en: [0, 3], tiles: 'tiles_cosmo', col: 1 },
    ship: { label: '3 VAISSEAU', en: [0, 7], tiles: 'tiles_ship', col: 2 },
  };
  function drawPreview(c, t) {
    const th = c.dataset.theme, P = PREV[th], sc = SCENES[th];
    const x = c.getContext('2d');
    x.imageSmoothingEnabled = false;
    const cw = c.width, ch = c.height;
    const sky = img(sc.sky);
    if (!sky) return false;
    // ciel (bas de l'image 540 → proche de l'horizon)
    x.drawImage(sky, 0, 540 - 250, sky.width, 250, 0, 0, cw * 2, ch);
    for (const [key, y, speed] of sc.layers) {
      const im = img(key);
      if (!im) continue;
      const off = Math.floor((t * speed * 0.8) % im.width);
      x.drawImage(im, off, 0, cw, im.height, 0, Math.round((y - 540 + 250) * (ch / 250)) + 6, cw, Math.round(im.height * (ch / 250)));
      if (off + cw > im.width) x.drawImage(im, 0, 0, cw, im.height, im.width - off, Math.round((y - 540 + 250) * (ch / 250)) + 6, cw, Math.round(im.height * (ch / 250)));
    }
    // sol : haut des tuiles herbe
    const tl = img(P.tiles);
    if (tl) for (let gx = -((t * 20) % 20); gx < cw; gx += 20) x.drawImage(tl, 40, 0, 40, 40, Math.floor(gx), ch - 14, 20, 20);
    // ennemi qui marche + pistache
    const en = img('enemies');
    if (en) {
      const fr = Math.floor(t * 6) % 4;
      x.drawImage(en, fr * 48, P.en[1] * 48, 48, 48, cw - 44, ch - 14 - 32, 32, 32);
    }
    const it = img('items');
    if (it) x.drawImage(it, (Math.floor(t * 10) % 8) * 24, 0, 24, 24, 10, ch - 40 + Math.round(Math.sin(t * 3) * 3), 16, 16);
    // étiquette pixel
    x.fillStyle = 'rgba(8,14,8,0.72)';
    x.fillRect(0, 0, cw, 13);
    if (window.GFX && GFX.text) GFX.text(x, P.label, cw / 2, 2, 1, th === 'cosmo' ? 0 : th === 'ship' ? 2 : 1, 'center');
    return true;
  }

  // ---------------------------------------------------------------- vignette + scanlines
  let vign = null, scan = null;
  function overlays() {
    if (!vign) {
      vign = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.35, W / 2, H / 2, Math.max(W, H) * 0.75);
      vign.addColorStop(0, 'rgba(0,0,0,0)');
      vign.addColorStop(1, 'rgba(0,0,0,0.45)');
    }
    ctx.fillStyle = vign; ctx.fillRect(0, 0, W, H);
    if (!scan) {
      const p = document.createElement('canvas'); p.width = 2; p.height = 3;
      const q = p.getContext('2d'); q.fillStyle = 'rgba(0,0,0,0.12)'; q.fillRect(0, 2, 2, 1);
      scan = ctx.createPattern(p, 'repeat');
    }
    ctx.fillStyle = scan; ctx.fillRect(0, 0, W, H);
  }

  // ---------------------------------------------------------------- boucle
  let prevT = 0;
  function frame(ts) {
    raf = 0;
    if (!MENU.active) return;
    const dt = Math.min(0.05, last ? (ts - last) / 1000 : 0.016);
    last = ts; T += dt;
    if (!(window.GFX && GFX.img && GFX.img.sousouHD && GFX.img.park_sky)) { raf = requestAnimationFrame(frame); return; }
    if (!scr.classList.contains('fx-on')) { scr.classList.add('fx-on'); resize(); initNuts(); }
    const cyc = 10, k = Math.floor(T / cyc) % 3, p = (T % cyc) / cyc;
    const th = THEMES[k];
    ctx.fillStyle = '#0d1a0c'; ctx.fillRect(0, 0, W, H);
    drawScene(th, T, 1);
    if (p > 0.9) drawScene(THEMES[(k + 1) % 3], T, (p - 0.9) / 0.1);
    drawNuts(dt, false);
    stepSousou(dt);
    drawStage(dt, p > 0.95 ? THEMES[(k + 1) % 3] : th);
    drawNuts(dt, true);
    drawLogo(T);
    overlays();
    if (T - prevT > 0.12) { prevT = T; previews.forEach((c) => drawPreview(c, T)); }
    raf = requestAnimationFrame(frame);
  }
  function setActive(on) {
    if (on === MENU.active) return;
    MENU.active = on;
    if (on) { last = 0; resize(); if (!raf) raf = requestAnimationFrame(frame); }
  }
  const sync = () => setActive(!scr.classList.contains('hidden'));
  new MutationObserver(sync).observe(scr, { attributes: true, attributeFilter: ['class'] });
  window.addEventListener('resize', () => { if (MENU.active) { resize(); } });
  window.addEventListener('orientationchange', () => setTimeout(() => { if (MENU.active) resize(); }, 200));
  document.addEventListener('visibilitychange', () => { if (document.hidden) setActive(false); else sync(); });
  // la mise en page (grand texte, polices) peut changer les emplacements
  if (window.ResizeObserver) new ResizeObserver(() => { if (MENU.active) resize(); }).observe(scr.querySelector('.m2') || scr);
  sync();
})();
