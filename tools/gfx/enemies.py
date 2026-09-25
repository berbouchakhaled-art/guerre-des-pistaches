import math
from px import *

OUT = (34, 20, 18)
PEA = [(88, 54, 32), (130, 86, 50), (172, 124, 74), (208, 164, 102), (236, 204, 146)]
PEA_ANGRY = [(96, 44, 30), (146, 72, 44), (188, 108, 64), (220, 150, 94), (240, 190, 136)]
SHOE = [(40, 26, 22), (70, 46, 36), (100, 70, 54)]
ARMY = [(34, 52, 26), (56, 82, 38), (84, 116, 52), (118, 150, 70), (150, 180, 96)]
RAIS = [(26, 12, 28), (52, 24, 50), (80, 40, 74), (110, 60, 98), (146, 92, 128)]
ALIEN = [(30, 90, 20), (70, 170, 40), (140, 230, 70), (210, 255, 150)]

def lobe_shade(img, cx, cy, rx, ry, ramp, tex=True, seed=0):
    for (x, y, dx, dy) in ellipse_pts(cx, cy, rx, ry):
        t = 0.18 + 0.82 * sphere_light(dx, dy)
        c = ramp_pick(ramp, t, x, y)
        if tex:
            # peanut shell lattice: small darker pits in a staggered grid
            gx = (x + (y // 3) % 2 * 2) % 4; gy = y % 3
            if gx == 0 and gy == 0 and t < 0.92:
                i = ramp.index(c) if c in ramp else 2
                c = ramp[max(0, i - 1)]
        put(img, x, y, c)

def eye(img, x, y, pupil_dx=1, angry=False, big=False):
    W = (250, 250, 244); P = (24, 16, 16)
    w, h = (4, 5) if big else (3, 4)
    rect(img, x, y, w, h, W)
    put(img, x, y, OUT); put(img, x + w - 1, y, OUT) if not big else None
    px_ = x + w - 2 + (0 if pupil_dx > 0 else -1)
    rect(img, px_, y + 1, 2, h - 2 if not big else 3, P)
    put(img, px_, y + 1, (255, 255, 255)) if big else None
    if angry:
        for i in range(w + 1):
            put(img, x - 1 + i, y - 1 + (i if i < w else w - 1) // 2 - 0, OUT)

def peanut(frame, variant='peanut', scale=1.0, space=False):
    im = new(48, 48)
    ramp = PEA_ANGRY if variant == 'angry' else PEA
    s = scale
    bob = [0, -1, 0, -1][frame]
    base = 45                    # feet bottom
    cx = 24
    # feet (behind body a bit)
    step = [(-2, 0, 2, -1), (0, -1, 0, 0), (2, -1, -2, 0), (0, 0, 0, -1)][frame]
    for (fx, fy) in [(cx - 6 * s + step[0], base - 2 + step[1]), (cx + 3 * s + step[2], base - 2 + step[3])]:
        rect(im, int(fx) + 2, int(fy) - 4, 2, 5, ramp[1])
        rect(im, int(fx), int(fy), int(6 * s) + 1, 3, SHOE[1]); rect(im, int(fx), int(fy), int(6 * s) + 1, 1, SHOE[2])
    body = new(48, 48)
    ly = base - 4 - 10 * s + bob
    uy = ly - 12 * s
    lobe_shade(body, cx, ly, 10.5 * s, 10 * s, ramp)
    lobe_shade(body, cx + 1, uy, 9.2 * s, 9.2 * s, ramp)
    # waist crease
    for x in range(int(cx - 8 * s), int(cx + 9 * s)):
        yy = int(ly - 5.2 * s + 0.5 * math.sin(x))
        if get_a(body, x, yy): put(body, x, yy, ramp[1])
    blit_fast(im, body, 0, 0)
    # stubby arms swinging
    sw = [1, 0, -1, 0][frame]
    for side, ax in ((-1, cx - 11 * s), (1, cx + 10 * s)):
        ay = ly - 2 * s + (sw * side)
        rect(im, int(ax), int(ay), 2, 4, ramp[1])
    # face on upper lobe (facing right)
    ex = int(cx + 1 + 1 * s); ey = int(uy - 2 * s)
    big = s > 1.1
    eye(im, ex - int(4 * s), ey, angry=(variant != 'peanut'), big=big)
    eye(im, ex + int(2 * s) + 1, ey, angry=(variant != 'peanut'), big=big)
    my = ey + (6 if not big else 8)
    mx = ex + int(1 * s)
    if variant == 'peanut':
        rect(im, mx - 1, my, 4, 1, OUT)        # grumpy flat mouth
        put(im, mx - 2, my + 1, OUT)
    else:
        rect(im, mx - 1, my, 4, 1, OUT); put(im, mx - 2, my + 1, OUT); put(im, mx + 3, my + 1, OUT)
        put(im, mx, my + 1, (240, 240, 230)); put(im, mx + 1, my + 1, (240, 240, 230))  # teeth grit
    if variant == 'angry':
        # red headband with fluttering tails
        by = int(uy - 7 * s)
        for x in range(int(cx - 9 * s), int(cx + 10 * s) + 1):
            for yy in (by, by + 1):
                if get_a(im, x, yy): put(im, x, yy, (212, 40, 40) if yy == by else (150, 24, 30))
        tx = int(cx - 9 * s)
        fl = [0, 1, 0, -1][frame]
        for i in range(5):
            put(im, tx - 1 - i, by + i // 2 + (fl if i > 2 else 0), (212, 40, 40))
            put(im, tx - 1 - i, by + 1 + i // 2 + (fl if i > 2 else 0), (150, 24, 30))
    if variant == 'jumbo':
        # army helmet
        hy = uy - 4 * s
        for (x, y, dx, dy) in ellipse_pts(cx + 1, hy, 11 * s, 7.5 * s):
            if dy <= 0.25:
                t = 0.2 + 0.8 * sphere_light(dx, dy)
                put(im, x, y, ramp_pick(ARMY, t, x, y))
        rect(im, int(cx - 11 * s), int(hy + 1), int(23 * s), 2, ARMY[1])
        # star emblem
        put(im, int(cx + 2), int(hy - 4), (250, 220, 90)); put(im, int(cx + 1), int(hy - 3), (250, 220, 90)); put(im, int(cx + 3), int(hy - 3), (250, 220, 90))
        # chin strap
        for yy in range(int(hy + 3), int(ey + 7)):
            put(im, int(cx - 7 * s), yy, (60, 44, 30))
    if space:
        # glass bubble helmet around upper lobe
        hcx, hcy, r = cx + 1, uy - (1 if variant != 'jumbo' else 3), (12.5 if variant != 'jumbo' else 15.5) * (s if variant != 'jumbo' else 1)
        glass = new(48, 48)
        for (x, y, dx, dy) in ellipse_pts(hcx, hcy, r, r):
            d = dx * dx + dy * dy
            if d > 0.78:
                put(glass, x, y, (180, 230, 255), 150)
        # highlight arc
        for a in range(200, 260, 6):
            ar = math.radians(a)
            put(glass, int(hcx + math.cos(ar) * (r - 3)), int(hcy + math.sin(ar) * (r - 3)), (255, 255, 255), 230)
        put(glass, int(hcx - r * 0.45), int(hcy - r * 0.2), (255, 255, 255), 230)
        blit_fast(im, glass, 0, 0)
        # collar ring
        rect(im, int(hcx - 8), int(hcy + r - 2), 17, 2, (150, 160, 176))
        rect(im, int(hcx - 8), int(hcy + r - 1), 17, 1, (90, 96, 116))
    outline(im, OUT)
    return im

def flyer(frame):
    """space peanut with a jetpack (cosmo flyer), centred at (24,24)"""
    im = new(48, 48)
    bob = [0, -1, -1, 0][frame]
    cx, cy = 24, 26 + bob
    # jetpack (behind, on the left since it faces right)
    rect(im, cx - 13, cy - 8, 5, 12, (120, 130, 150)); rect(im, cx - 13, cy - 8, 5, 2, (180, 190, 205))
    rect(im, cx - 12, cy + 4, 3, 2, (70, 74, 90))
    flame = [(255, 250, 200), (255, 200, 80), (240, 110, 40)]
    fl = [5, 7, 4, 6][frame]
    for i in range(fl):
        w = 2 if i < fl - 2 else 1
        rect(im, cx - 12 + (1 - w // 2) - 0, cy + 6 + i, w + 1 if i < 2 else w, 1, flame[min(2, i // 2)])
    body = peanut(1, 'angry', 0.8, space=True)
    blit_fast(im, body, 0, int(cy - 34))
    outline(im, OUT)
    return im

def raisin(frame, boss=False):
    im = new(48, 48)
    s = 1.3 if boss else 1.0
    bob = [0, -1, 0, -1][frame]
    base = 45; cx = 24
    # legs
    step = [(-2, 0, 2, -1), (0, -1, 0, 0), (2, -1, -2, 0), (0, 0, 0, -1)][frame]
    for (fx, fy) in [(cx - 6 * s + step[0], base - 3 + step[1]), (cx + 2 * s + step[2], base - 3 + step[3])]:
        rect(im, int(fx) + 1, int(fy) - 2, 2, 3, RAIS[0])
        rect(im, int(fx), int(fy) + 1, 5, 2, (20, 60, 20)); rect(im, int(fx), int(fy) + 1, 5, 1, (60, 130, 40))
    body = new(48, 48)
    cy = base - 4 - 13 * s + bob
    rx, ry = 12 * s, 13 * s
    for (x, y, dx, dy) in ellipse_pts(cx, cy, rx, ry):
        # wrinkles: wavy bands
        w = math.sin(dy * 7.5 + 2.2 * math.sin(dx * 3.1 + 1.3) + dx * 1.2)
        t = 0.15 + 0.85 * sphere_light(dx, dy)
        if w > 0.72: t -= 0.28
        elif w < -0.85: t += 0.1
        put(body, x, y, ramp_pick(RAIS, t, x, y))
    blit_fast(im, body, 0, 0)
    # antennae
    for (ax, lean) in ((cx - 3, -1), (cx + 5, 1)):
        top = int(cy - ry - 5 * s)
        for yy in range(top, int(cy - ry + 3)):
            put(im, ax + (lean if yy < top + 3 else 0), yy, RAIS[1])
        g = ALIEN[2] if frame % 2 == 0 else ALIEN[3]
        rect(im, ax + lean - 1, top - 2, 3, 3, g); put(im, ax + lean - 1, top - 2, ALIEN[3])
    if boss:
        cx3 = cx + 1
        top = int(cy - ry - 7)
        for yy in range(top, int(cy - ry + 2)): put(im, cx3, yy, RAIS[1])
        rect(im, cx3 - 1, top - 2, 3, 3, (255, 90, 90))
    # big alien eyes facing right
    ey = int(cy - 4 * s)
    for (ex, w) in ((int(cx + 1 * s), int(5 * s)), (int(cx + 7 * s), int(4 * s))):
        for (x, y, dx, dy) in ellipse_pts(ex + w / 2, ey + 3 * s, w / 2 + 0.3, 3.4 * s):
            t = 0.3 + 0.7 * sphere_light(dx, dy)
            put(im, x, y, ramp_pick(ALIEN, t, x, y, False))
        rect(im, ex + w - 2, int(ey + 2 * s), 2, int(3 * s), (10, 30, 10))
        put(im, ex + 1, int(ey + 1 * s), (240, 255, 220))
    if boss:
        # red visor band across the eyes
        for x in range(int(cx - 2), int(cx + 14 * s) - 3):
            for yy in range(int(ey + 1), int(ey + 5 * s)):
                if get_a(im, x, yy):
                    v = (230, 40, 60) if yy < ey + 3 else (150, 20, 40)
                    put(im, x, yy, v)
        for x in range(int(cx + 1), int(cx + 12)):
            if x % 3 == frame % 3: put(im, x, int(ey + 2), (255, 180, 180))
    # mouth
    my = int(cy + 5 * s)
    rect(im, int(cx + 4 * s), my, int(4 * s), 1, (255, 140, 110))
    put(im, int(cx + 4 * s) - 1, my - 1, (255, 140, 110))
    outline(im, OUT)
    return im

def ufo(frame):
    im = new(48, 48)
    bob = [0, -1, -1, 0][frame]
    r = raisin(1)
    small = resample(r, 32, 32)
    # raisin pilot sitting in a dome
    blit_fast(im, small, 8, 2 + bob)
    # glass dome
    for (x, y, dx, dy) in ellipse_pts(24, 24 + bob, 11, 11):
        if dy < 0.35 and dx * dx + dy * dy > 0.8:
            put(im, x, y, (170, 240, 220), 140)
    put(im, 17, 16 + bob, (255, 255, 255), 230); put(im, 18, 15 + bob, (255, 255, 255), 230)
    # saucer
    METAL = [(50, 60, 66), (86, 100, 104), (130, 146, 146), (180, 196, 190), (230, 240, 232)]
    for (x, y, dx, dy) in ellipse_pts(24, 30 + bob, 20, 5.5):
        t = 0.2 + 0.8 * sphere_light(dx * 0.7, dy)
        put(im, x, y, ramp_pick(METAL, t, x, y))
    rect(im, 6, 30 + bob, 37, 1, METAL[1])
    # running lights
    cols = [(255, 80, 80), (255, 230, 80), (120, 255, 120), (100, 200, 255)]
    for i in range(5):
        c = cols[(i + frame) % 4]
        put(im, 10 + i * 7, 31 + bob, c); put(im, 11 + i * 7, 31 + bob, c)
    # tractor beam flicker
    if frame % 2 == 0:
        for y in range(36 + bob, 44):
            w = (y - 34) // 2
            for x in range(24 - w, 25 + w):
                if (x + y) % 2 == 0: put(im, x, y, (160, 255, 160), 90)
    outline(im, OUT, only_alpha_above=120)
    return im

def squash(img, anchor_bottom=45):
    """flattened death sprite from a frame"""
    a = img[:, :, 3] > 0
    ys, xs = np.nonzero(a)
    crop = img[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = crop.shape[:2]
    nw, nh = min(46, int(w * 1.35)), max(6, int(h * 0.38))
    sq = resample(crop, nw, nh)
    out = new(48, 48)
    blit_fast(out, sq, 24 - nw // 2, anchor_bottom + 1 - nh)
    return out

ROWS = ['peanut', 'angry', 'jumbo', 'peanut_s', 'angry_s', 'jumbo_s', 'flyer', 'raisin', 'ufo', 'boss']

def build(outdir):
    cells = []
    for r in ROWS:
        fr = []
        for f in range(4):
            if r == 'peanut': fr.append(peanut(f, 'peanut'))
            elif r == 'angry': fr.append(peanut(f, 'angry', 1.05))
            elif r == 'jumbo': fr.append(peanut(f, 'jumbo', 1.25))
            elif r == 'peanut_s': fr.append(peanut(f, 'peanut', space=True))
            elif r == 'angry_s': fr.append(peanut(f, 'angry', 1.05, space=True))
            elif r == 'jumbo_s': fr.append(peanut(f, 'jumbo', 1.25, space=True))
            elif r == 'flyer': fr.append(flyer(f))
            elif r == 'raisin': fr.append(raisin(f))
            elif r == 'ufo': fr.append(ufo(f))
            elif r == 'boss': fr.append(raisin(f, boss=True))
        fr.append(squash(fr[0], 45 if r not in ('flyer', 'ufo') else 34))
        cells += fr
    save(sheet(cells, 48, 48, 5), outdir + '/enemies.png')

if __name__ == '__main__':
    import sys
    build(sys.argv[1])
