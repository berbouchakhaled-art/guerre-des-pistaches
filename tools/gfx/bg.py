import math
import numpy as np
from px import *

W = 1024
B4 = np.array(BAYER4, np.float32)

def np_hash(ix, iy, s):
    n = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + s * 2246822519) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFFFF).astype(np.float64) / float(0x1000000)

def np_vnoise(X, Y, s, scale, period=None):
    fx, fy = X / scale, Y / scale
    x0 = np.floor(fx); y0 = np.floor(fy)
    tx = fx - x0; ty = fy - y0
    tx = tx * tx * (3 - 2 * tx); ty = ty * ty * (3 - 2 * ty)
    x1 = x0 + 1
    if period:
        p = max(1, int(round(period / scale)))
        x0 = np.mod(x0, p); x1 = np.mod(x1, p)
    a = np_hash(x0, y0, s); b = np_hash(x1, y0, s); c = np_hash(x0, y0 + 1, s); d = np_hash(x1, y0 + 1, s)
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty

def np_fbm(X, Y, s, scale, oct=4, period=None):
    v = 0; amp = 0.5; tot = 0
    for i in range(oct):
        v = v + np_vnoise(X, Y, s + i * 17, scale, period) * amp; tot += amp
        amp *= 0.5; scale /= 2
    return v / tot

def ramp_img(ramp, T, dither=True):
    """T: HxW float array in [0,1] -> HxWx3 using ramp with Bayer dithering"""
    H, Wd = T.shape
    R = np.array(ramp, np.uint8)
    f = np.clip(T, 0, 0.9999) * (len(ramp) - 1)
    i = np.floor(f).astype(int); fr = f - i
    if dither:
        yy, xx = np.mgrid[0:H, 0:Wd]
        th = (B4[yy & 3, xx & 3] + 0.5) / 16.0
        i = np.where((fr > th) & (i + 1 < len(ramp)), i + 1, i)
    return R[i]

def grid(w, h):
    Y, X = np.mgrid[0:h, 0:w].astype(np.float64)
    return X, Y

def to_rgba(rgb, alpha):
    out = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    out[:, :, :3] = rgb; out[:, :, 3] = alpha
    return out

def ridge(x, seed, base, amps):
    """periodic silhouette height over W"""
    h = np.full_like(x, base, dtype=np.float64)
    for i, (per, amp) in enumerate(amps):
        ph = hsh(i, seed, 1) * math.tau
        h += amp * np.sin(x * math.tau * per / W + ph)
    return h

# ---------------------------------------------------------------- PARK
def park_sky():
    X, Y = grid(960, 540)
    ramp = [(58, 122, 214), (70, 140, 224), (86, 160, 232), (108, 180, 238), (134, 198, 242), (162, 214, 244), (190, 228, 246), (214, 238, 246)]
    t = (Y / 470.0) ** 1.15
    rgb = ramp_img(ramp, t)
    img = to_rgba(rgb, 255)
    # sun with dithered halo
    cx, cy = 790, 92
    d = np.hypot(X - cx, Y - cy)
    halo = np.clip(1 - (d - 26) / 70, 0, 1)
    th = (B4[Y.astype(int) & 3, X.astype(int) & 3] + 0.5) / 16
    m1 = (halo * 0.55 > th) & (d > 26)
    img[m1, :3] = np.clip(img[m1, :3].astype(int) + 22, 0, 255).astype(np.uint8)
    core = d <= 26
    img[core, :3] = (255, 244, 170)
    img[(d <= 22) & core, :3] = (255, 252, 214)
    img[(d > 24) & core, :3] = (255, 214, 110)
    return img

def cloud(img, cx, cy, s, seed):
    ramp = [(150, 186, 220), (188, 214, 236), (222, 236, 248), (246, 250, 255), (255, 255, 255)]
    blobs = [(0, 0, 1.0), (-1.0, 0.25, 0.75), (1.05, 0.2, 0.8), (-0.45, -0.45, 0.8), (0.5, -0.5, 0.72), (1.7, 0.4, 0.5), (-1.7, 0.45, 0.5)]
    lay = new(img.shape[1], img.shape[0])
    for (bx, by, r) in blobs:
        rr = r * s * (0.85 + 0.3 * hsh(bx * 10, by * 10, seed))
        shaded_ellipse(lay, cx + bx * s * 1.1, cy + by * s, rr * 1.15, rr, ramp, amb=0.45, light=(-0.3, -0.9, 0.4))
    # flat bottom
    lay[int(cy + s * 0.55):, :, 3] = 0
    blit_fast(img, lay, 0, 0)

def park_clouds():
    img = new(W, 200)
    spots = [(90, 70, 26), (330, 120, 18), (520, 60, 30), (760, 130, 16), (900, 80, 22)]
    for i, (x, y, s) in enumerate(spots):
        for off in (-W, 0, W):
            if -150 < x + off < W + 150:
                cloud(img, x + off, y, s, i)
    return img

def park_far():
    H = 260
    X, Y = grid(W, H)
    img = new(W, H)
    # far mountains (bluish) + nearer hills (teal-green)
    h1 = ridge(X[0], 11, 120, [(2, 26), (5, 14), (11, 6)])
    h2 = ridge(X[0], 12, 170, [(3, 18), (7, 9), (13, 4)])
    m1 = Y >= h1[None, :]
    m2 = Y >= h2[None, :]
    far = [(118, 164, 200), (132, 178, 208), (148, 192, 214), (168, 206, 220)]
    near = [(84, 150, 150), (98, 166, 150), (114, 182, 150), (134, 196, 156)]
    t1 = 0.75 - (Y - h1[None, :]) / 120 + np_fbm(X, Y, 3, 40, 3, W) * 0.3
    t2 = 0.8 - (Y - h2[None, :]) / 90 + np_fbm(X, Y, 4, 30, 3, W) * 0.3
    rgb1 = ramp_img(far, t1); rgb2 = ramp_img(near, t2)
    img[m1, :3] = rgb1[m1]; img[m1, 3] = 255
    img[m2, :3] = rgb2[m2]; img[m2, 3] = 255
    # snow caps / rim light on mountain tops
    top1 = (Y >= h1[None, :]) & (Y < h1[None, :] + 2)
    img[top1 & ~m2, :3] = (196, 222, 232)
    top2 = (Y >= h2[None, :]) & (Y < h2[None, :] + 1)
    img[top2, :3] = (160, 206, 170)
    return img

def tree_round(img, x, base, h, r, seed, pistachio=False):
    trunk = [(50, 34, 26), (78, 54, 38), (108, 76, 52)]
    leaf = [(22, 70, 40), (34, 100, 46), (56, 134, 54), (90, 168, 62), (136, 200, 84)] if not pistachio else \
           [(30, 74, 38), (46, 108, 48), (74, 142, 58), (112, 176, 70), (160, 206, 100)]
    for y in range(int(base - h), int(base)):
        w = 2 if y > base - h * 0.6 else 1
        for dx in range(-w, w + 1):
            put(img, int(x + dx), y, trunk[1] if dx < 0 else trunk[2])
        put(img, int(x - w - 1), y, trunk[0])
    if pistachio:
        # gnarled branches
        for sgn in (-1, 1):
            for k in range(int(r * 0.7)):
                put(img, int(x + sgn * k), int(base - h * 0.7 - k * 0.6), trunk[1])
    cy = base - h - r * 0.4
    blobs = [(0, 0, 1.0), (-0.7, 0.35, 0.7), (0.7, 0.3, 0.72), (0, -0.55, 0.7)] if not pistachio else \
            [(0, 0, 0.9), (-0.9, 0.25, 0.65), (0.9, 0.2, 0.65), (-0.4, -0.5, 0.6), (0.45, -0.45, 0.62)]
    lay = new(img.shape[1], img.shape[0])
    for (bx, by, s) in blobs:
        rr = r * s
        for (px_, py_, dx, dy) in ellipse_pts(x + bx * r, cy + by * r, rr, rr * 0.92):
            n = hsh(px_ // 2, py_ // 2, seed)
            t = 0.12 + 0.88 * sphere_light(dx, dy) + (n - 0.5) * 0.25
            put(lay, px_, py_, ramp_pick(leaf, t, px_, py_))
    if pistachio:
        # clusters of pink-beige pistachio nuts
        for k in range(14):
            nx = x + (hsh(k, seed, 5) - 0.5) * r * 2.2; ny = cy + (hsh(k, seed, 6) - 0.4) * r * 1.4
            if get_a(lay, int(nx), int(ny)):
                put(lay, int(nx), int(ny), (236, 196, 176)); put(lay, int(nx) + 1, int(ny), (206, 150, 140)); put(lay, int(nx), int(ny) + 1, (190, 130, 124))
    outline(lay, (18, 44, 30))
    blit_fast(img, lay, 0, 0)

def park_mid():
    H = 300
    X, Y = grid(W, H)
    img = new(W, H)
    h = ridge(X[0], 21, 210, [(2, 16), (4, 10), (9, 4)])
    m = Y >= h[None, :]
    ramp = [(40, 110, 56), (54, 130, 60), (70, 150, 64), (92, 170, 70), (120, 190, 84)]
    t = 0.85 - (Y - h[None, :]) / 70 + np_fbm(X, Y, 7, 24, 3, W) * 0.25
    rgb = ramp_img(ramp, t)
    img[m, :3] = rgb[m]; img[m, 3] = 255
    top = (Y >= h[None, :]) & (Y < h[None, :] + 1)
    img[top, :3] = (150, 210, 110)
    trees = [(60, 1, 30, 22), (170, 0, 36, 26), (300, 1, 26, 20), (420, 0, 40, 28), (560, 1, 30, 24), (650, 0, 34, 22), (780, 1, 28, 22), (900, 0, 38, 27), (990, 1, 26, 20)]
    for i, (tx, pist, th, r) in enumerate(trees):
        base = h[int(tx) % W] + 6
        for off in (-W, 0, W):
            if -80 < tx + off < W + 80:
                tree_round(img, tx + off, base, th, r, i, pistachio=bool(pist))
    return img

def park_near():
    H = 150
    X, Y = grid(W, H)
    img = new(W, H)
    # bush line
    h = ridge(X[0], 31, 70, [(6, 10), (13, 6), (29, 3)])
    m = Y >= h[None, :]
    ramp = [(20, 64, 36), (30, 86, 42), (44, 110, 48), (64, 136, 56), (92, 160, 66)]
    t = 0.8 - (Y - h[None, :]) / 50 + np_fbm(X, Y, 9, 10, 3, W) * 0.35
    rgb = ramp_img(ramp, t)
    img[m, :3] = rgb[m]; img[m, 3] = 255
    # flowers in bushes
    for k in range(60):
        fx = int(hsh(k, 1, 33) * W); fy = int(h[fx] + 6 + hsh(k, 2, 33) * 30)
        col = [(255, 240, 120), (255, 150, 170), (250, 250, 250), (200, 170, 255)][k % 4]
        put(img, fx, fy, col); put(img, fx + 1, fy, mix(col, (0, 0, 0), 0.25))
    # wooden fence
    fence = [(90, 60, 40), (140, 100, 64), (186, 142, 96)]
    for fx in range(0, W, 48):
        for y in range(62, 110):
            for dx in range(4):
                put(img, fx + 10 + dx, y, fence[1] if dx < 2 else fence[2])
            put(img, fx + 9, y, fence[0]); put(img, fx + 14, y, fence[0])
        rect(img, fx + 9, 60, 6, 2, fence[0])
    for y0 in (72, 90):
        for x in range(W):
            put(img, x, y0, fence[2]); put(img, x, y0 + 1, fence[1]); put(img, x, y0 + 2, fence[1]); put(img, x, y0 + 3, fence[0])
    # re-draw bushes in front of fence bottom
    h2 = ridge(X[0], 32, 100, [(7, 6), (15, 4), (31, 2)])
    m2 = Y >= h2[None, :]
    t2 = 0.7 - (Y - h2[None, :]) / 40 + np_fbm(X, Y, 10, 8, 3, W) * 0.35
    rgb2 = ramp_img(ramp, t2)
    img[m2, :3] = rgb2[m2]; img[m2, 3] = 255
    return img

# ---------------------------------------------------------------- COSMO
def space_sky(palette, seed, nebula_cols):
    X, Y = grid(960, 540)
    t = (Y / 540.0)
    rgb = ramp_img(palette, t * 0.9 + np_fbm(X, Y, seed, 120, 3) * 0.15)
    img = to_rgba(rgb, 255)
    # nebula clouds (two colours)
    for k, (cols, sc, thr) in enumerate(nebula_cols):
        n = np_fbm(X, Y, seed + 10 + k * 7, sc, 5)
        v = np.clip((n - thr) / (1 - thr), 0, 1)
        th = (B4[Y.astype(int) & 3, X.astype(int) & 3] + 0.5) / 16
        for lvl, c in enumerate(cols):
            m = v * len(cols) > (lvl + th)
            img[m, :3] = c
    # static faint stars
    for i in range(260):
        x = int(hsh(i, 1, seed) * 960); y = int(hsh(i, 2, seed) * 540)
        b = hsh(i, 3, seed)
        c = (120, 110, 160) if b < 0.6 else ((200, 190, 230) if b < 0.9 else (255, 255, 255))
        put(img, x, y, c)
    return img

def cosmo_sky():
    pal = [(6, 4, 20), (12, 8, 34), (20, 12, 50), (30, 16, 66), (44, 20, 82), (60, 24, 96)]
    neb = [([(56, 20, 90), (90, 30, 120), (140, 50, 150), (200, 90, 180)], 160, 0.52),
           ([(20, 50, 90), (30, 90, 130), (60, 150, 170)], 110, 0.6)]
    return space_sky(pal, 5, neb)

def planet(img, cx, cy, r, ramp, ring=None, bands=0, seed=0):
    lay = new(img.shape[1], img.shape[0])
    for (x, y, dx, dy) in ellipse_pts(cx, cy, r, r):
        t = 0.08 + 0.92 * sphere_light(dx, dy, (-0.7, -0.4, 0.6))
        if bands:
            t += 0.08 * math.sin(dy * bands + 2 * vnoise(x, y, seed, 12))
        put(lay, x, y, ramp_pick(ramp, t, x, y))
    if ring:
        rc = ring
        for a10 in range(0, 3600, 2):
            a = math.radians(a10 / 10)
            for rr in np.arange(r * 1.35, r * 1.9, 0.5):
                x = cx + math.cos(a) * rr; y = cy + math.sin(a) * rr * 0.28
                behind = math.sin(a) < 0
                xi, yi = int(x), int(y)
                if behind and get_a(lay, xi, yi) and ((xi - cx) ** 2 + (yi - cy) ** 2) < r * r: continue
                band = int((rr - r * 1.35) / 3) % 3
                put(lay, xi, yi, rc[band])
    outline(lay, (10, 6, 20))
    blit_fast(img, lay, 0, 0)

def cosmo_planets():
    H = 420
    img = new(W, H)
    # big pistachio-green ringed planet
    planet(img, 720, 150, 70, [(20, 50, 30), (40, 90, 46), (80, 140, 60), (130, 190, 80), (190, 230, 130)],
           ring=[(220, 190, 150), (180, 140, 110), (240, 220, 190)], bands=9, seed=3)
    # small pink moon + tiny blue moon
    planet(img, 220, 90, 26, [(60, 20, 50), (120, 40, 90), (190, 80, 140), (240, 150, 190), (255, 210, 230)], seed=4)
    planet(img, 420, 230, 11, [(20, 30, 70), (40, 70, 140), (90, 140, 210), (170, 210, 250)], seed=5)
    # craters on moon
    for (x, y, r) in [(214, 84, 4), (230, 98, 3), (206, 100, 2)]:
        for (px_, py_, dx, dy) in ellipse_pts(x, y, r, r * 0.8):
            put(img, px_, py_, (150, 60, 110) if dy < 0.2 else (220, 130, 170))
    return img

def cosmo_far():
    H = 240
    X, Y = grid(W, H)
    img = new(W, H)
    rock = [(24, 14, 44), (36, 22, 62), (52, 32, 84), (74, 48, 110)]
    rim = (150, 110, 200)
    # floating asteroids
    for i in range(9):
        cx = hsh(i, 1, 70) * W; cy = 30 + hsh(i, 2, 70) * 110; r = 8 + hsh(i, 3, 70) * 18
        for off in (-W, 0, W):
            if -60 < cx + off < W + 60:
                lay = new(W, H)
                for (x, y, dx, dy) in ellipse_pts(cx + off, cy, r * 1.3, r):
                    n = vnoise(x, y, i, 5)
                    if dx * dx + dy * dy > 0.75 + n * 0.25: continue
                    t = 0.1 + 0.9 * sphere_light(dx, dy, (-0.6, -0.6, 0.5))
                    put(lay, x, y, ramp_pick(rock, t, x, y))
                inner_edge(lay, rim)
                blit_fast(img, lay, 0, 0)
    # distant jagged horizon
    h = ridge(X[0], 41, 200, [(5, 12), (11, 8), (23, 5), (47, 3)])
    m = Y >= h[None, :]
    rgb = ramp_img(rock, 0.55 - (Y - h[None, :]) / 60)
    img[m, :3] = rgb[m]; img[m, 3] = 255
    top = (Y >= h[None, :]) & (Y < h[None, :] + 1)
    img[top, :3] = rim
    return img

def crystal(img, x, base, h, w, cols, lean=0):
    pts = [(x - w, base), (x - w * 0.6 + lean * 0.5, base - h * 0.75), (x + lean, base - h), (x + w * 0.6 + lean * 0.5, base - h * 0.75), (x + w, base)]
    poly_fill(img, pts, cols[1])
    poly_fill(img, [(x + lean, base - h), (x + w * 0.6 + lean * 0.5, base - h * 0.75), (x + w, base), (x + lean * 0.3, base)], cols[2])
    line(img, x + lean, base - h, x + lean * 0.3, base, cols[3])

def cosmo_near():
    H = 220
    X, Y = grid(W, H)
    img = new(W, H)
    dark = [(14, 8, 28), (22, 12, 42), (32, 18, 58)]
    cyan = [(20, 70, 100), (40, 140, 170), (110, 220, 230), (230, 255, 255)]
    pink = [(90, 20, 90), (170, 50, 160), (240, 120, 220), (255, 220, 250)]
    lay = new(W, H)
    for i in range(22):
        x = hsh(i, 1, 80) * W; h = 30 + hsh(i, 2, 80) * 90; w = 5 + hsh(i, 3, 80) * 9
        cols = cyan if i % 3 else pink
        for off in (-W, 0, W):
            if -40 < x + off < W + 40:
                crystal(lay, x + off, H - 40, h, w, cols, lean=(hsh(i, 4, 80) - 0.5) * 16)
    outline(lay, (8, 4, 16))
    blit_fast(img, lay, 0, 0)
    h = ridge(X[0], 51, 170, [(6, 8), (13, 5), (27, 3)])
    m = Y >= h[None, :]
    rgb = ramp_img(dark, 0.9 - (Y - h[None, :]) / 40)
    img[m, :3] = rgb[m]; img[m, 3] = 255
    top = (Y >= h[None, :]) & (Y < h[None, :] + 1)
    img[top, :3] = (70, 50, 110)
    return img

# ---------------------------------------------------------------- SHIP
def ship_space():
    pal = [(2, 6, 12), (4, 10, 18), (6, 14, 24), (10, 20, 30), (14, 26, 34)]
    neb = [([(10, 40, 30), (20, 70, 40), (40, 110, 60), (80, 160, 90)], 150, 0.55),
           ([(40, 20, 50), (70, 30, 70)], 90, 0.66)]
    img = space_sky(pal, 17, neb)
    planet(img, 700, 330, 120, [(40, 20, 40), (80, 40, 70), (130, 70, 100), (190, 120, 140), (240, 190, 190)], bands=14, seed=9)
    return img

def ship_wall(lights=None):
    H = 540
    img = new(W, H)
    M = [(14, 20, 20), (22, 32, 30), (32, 46, 42), (46, 62, 56), (64, 84, 74), (90, 112, 98)]
    X, Y = grid(W, H)
    t = 0.45 + np_fbm(X * 2, Y * 0.3, 60, 20, 2, W * 2) * 0.12
    rgb = ramp_img(M, t)
    img[:, :, :3] = rgb; img[:, :, 3] = 255
    # panel grid
    for x in range(0, W, 128):
        img[:, x, :3] = M[0]; img[:, x + 1, :3] = M[4]
    for y in (70, 190, 330, 450):
        img[y, :, :3] = M[0]; img[y + 1, :, :3] = M[4]
    # rivets
    for x in range(0, W, 128):
        for y in (78, 182, 338, 442):
            for dx in (8, 118):
                put(img, x + dx, y, M[5]); put(img, x + dx + 1, y + 1, M[0])
    # windows (transparent) with thick rounded frames
    wins = [(64, 100, 200, 170), (576, 100, 200, 170)]
    frameR = [(40, 50, 50), (80, 96, 90), (130, 150, 140), (180, 200, 186)]
    for (wx, wy, ww, wh) in wins:
        for y in range(wy - 10, wy + wh + 10):
            for x in range(wx - 10, wx + ww + 10):
                # rounded rect distance
                rx = max(wx + 20 - x, 0, x - (wx + ww - 20)); ry = max(wy + 20 - y, 0, y - (wy + wh - 20))
                d = math.hypot(rx, ry)
                if d <= 20:
                    img[y, x, 3] = 0
                elif d <= 30:
                    k = d - 20
                    c = frameR[3] if k < 2 else (frameR[2] if k < 5 else (frameR[1] if k < 8 else frameR[0]))
                    # light from top-left
                    if (y < wy + wh / 2) and k < 5: c = frameR[3]
                    img[y, x, :3] = c; img[y, x, 3] = 255
        # window bolts
        for (bx, by) in [(wx - 4, wy + wh // 2), (wx + ww + 3, wy + wh // 2), (wx + ww // 2, wy - 5), (wx + ww // 2, wy + wh + 4)]:
            rect(img, bx - 1, by - 1, 3, 3, frameR[3]); put(img, bx + 1, by + 1, frameR[0])
    # big pistachio-green pipes along top and bottom
    G = [(20, 50, 30), (36, 84, 44), (60, 124, 60), (100, 170, 84), (160, 220, 130)]
    for (py0, th) in ((20, 22), (478, 26)):
        for y in range(py0, py0 + th):
            u = (y - py0) / (th - 1)
            c = ramp_pick(G, 0.25 + 0.7 * math.sin(u * math.pi) ** 0.7 - (0.3 if u > 0.75 else 0), 0, y, False)
            img[y, :, :3] = c; img[y, :, 3] = 255
        for x in range(40, W, 160):
            rect(img, x, py0 - 3, 10, th + 6, (70, 84, 80)); rect(img, x + 1, py0 - 3, 3, th + 6, (130, 146, 136))
    # signage
    signs = [(330, 120, 'P'), (840, 120, 'S')]
    for (sx, sy, ch) in signs:
        rect(img, sx, sy, 60, 26, (230, 180, 40)); rect(img, sx + 2, sy + 2, 56, 22, (40, 40, 30))
        for i in range(0, 56, 8):
            rect(img, sx + 2 + i, sy + 20, 4, 4, (230, 180, 40))
    # consoles with screens (lit)
    for cx0 in (310, 820):
        rect(img, cx0, 360, 90, 80, M[1]); rect(img, cx0, 360, 90, 2, M[5])
        rect(img, cx0 + 8, 370, 74, 34, (8, 30, 20))
        for i in range(6):
            rect(img, cx0 + 12, 374 + i * 5, 20 + int(hsh(i, cx0, 3) * 40), 2, (80, 220, 120))
        for i in range(5):
            rect(img, cx0 + 10 + i * 15, 414, 8, 6, [(220, 60, 60), (240, 200, 60), (80, 200, 100), (80, 160, 240), (220, 60, 60)][i])
    return img

def ship_lights(phase):
    img = new(W, 540)
    pts = []
    for x in range(64, W, 128):
        pts.append((x, 60)); pts.append((x + 32, 462))
    for i, (x, y) in enumerate(pts):
        on = (i + phase) % 3 != 0
        c = [(255, 70, 70), (90, 255, 140), (255, 210, 70)][i % 3]
        if on:
            rect(img, x - 1, y - 1, 3, 3, c); put(img, x, y, (255, 255, 255))
            for (dx, dy) in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                put(img, x + dx, y + dy, c, 140)
        else:
            rect(img, x - 1, y - 1, 3, 3, mix(c, (0, 0, 0), 0.7))
    return img

def ship_mid():
    H = 300
    img = new(W, H)
    M = [(8, 12, 12), (14, 20, 20), (22, 32, 30), (34, 46, 42)]
    # vertical struts + diagonal braces (dark, foreground-ish)
    for x in range(0, W, 256):
        rect(img, x + 20, 0, 18, H, M[1]); rect(img, x + 20, 0, 3, H, M[3]); rect(img, x + 35, 0, 3, H, M[0])
        for k in range(0, H, 60):
            for i in range(60):
                for d in range(3):
                    put(img, x + 38 + i, k + i + d, M[2])
    # tanks / machinery silhouettes at the floor
    for i in range(6):
        tx = int(hsh(i, 5, 90) * W); tw = 40 + int(hsh(i, 6, 90) * 50); th = 50 + int(hsh(i, 7, 90) * 80)
        for off in (-W, 0, W):
            rect(img, tx + off, H - th, tw, th, M[2]); rect(img, tx + off, H - th, tw, 3, M[3])
            rect(img, tx + off + 6, H - th + 12, 6, 6, (60, 180, 90))
    return img

def build(outdir):
    save(park_sky(), outdir + '/bg_park_sky.png')
    save(park_clouds(), outdir + '/bg_park_clouds.png')
    save(park_far(), outdir + '/bg_park_far.png')
    save(park_mid(), outdir + '/bg_park_mid.png')
    save(park_near(), outdir + '/bg_park_near.png')
    save(cosmo_sky(), outdir + '/bg_cosmo_sky.png')
    save(cosmo_planets(), outdir + '/bg_cosmo_planets.png')
    save(cosmo_far(), outdir + '/bg_cosmo_far.png')
    save(cosmo_near(), outdir + '/bg_cosmo_near.png')
    save(ship_space(), outdir + '/bg_ship_space.png')
    save(ship_wall(), outdir + '/bg_ship_wall.png')
    save(ship_lights(0), outdir + '/bg_ship_lights0.png')
    save(ship_lights(1), outdir + '/bg_ship_lights1.png')
    save(ship_mid(), outdir + '/bg_ship_mid.png')

if __name__ == '__main__':
    import sys
    build(sys.argv[1])
