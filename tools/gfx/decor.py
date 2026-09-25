import math
from px import *
OUT = (26, 18, 22)

def flower(col, stem_h=9):
    im = new(32, 32)
    base = 31
    G = [(30, 80, 36), (56, 130, 50), (100, 180, 70)]
    for y in range(base - stem_h, base + 1):
        put(im, 16, y, G[1]); put(im, 15, y, G[0]) if y % 3 == 0 else None
    put(im, 17, base - 3, G[2]); put(im, 18, base - 4, G[2]); put(im, 14, base - 5, G[2])
    cy = base - stem_h - 2
    c2 = mix(col, (0, 0, 0), 0.3); c3 = mix(col, (255, 255, 255), 0.45)
    for (dx, dy) in ((0, -2), (2, 0), (0, 2), (-2, 0), (-1, -1), (1, -1), (1, 1), (-1, 1)):
        put(im, 16 + dx, cy + dy, col)
    put(im, 16, cy - 2, c3); put(im, 14, cy, c3)
    put(im, 17, cy + 2, c2); put(im, 18, cy, c2)
    put(im, 16, cy, (255, 220, 80))
    outline(im, OUT)
    return im

def tuft(seed, cols):
    im = new(32, 32)
    for k in range(7):
        x = 10 + k * 2 + (1 if hsh(k, seed, 1) > 0.5 else 0)
        h = 4 + int(hsh(k, seed, 2) * 6)
        lean = 1 if k > 3 else -1
        for i in range(h):
            put(im, x + (lean if i > h * 0.6 else 0), 31 - i, cols[2] if i > h - 3 else cols[1])
    outline(im, OUT)
    return im

def mushroom(cap, spots=True):
    im = new(32, 32)
    stem = [(200, 190, 170), (240, 232, 214)]
    rect(im, 14, 25, 4, 7, stem[1]); rect(im, 14, 25, 1, 7, stem[0])
    ramp = [mix(cap, (0, 0, 0), 0.5), mix(cap, (0, 0, 0), 0.25), cap, mix(cap, (255, 255, 255), 0.35)]
    for (x, y, dx, dy) in ellipse_pts(16, 25, 8, 6):
        if dy < 0.1:
            put(im, x, y, ramp_pick(ramp, 0.2 + 0.8 * sphere_light(dx, dy), x, y))
    if spots:
        for (x, y) in [(13, 21), (18, 20), (20, 23), (11, 24)]:
            put(im, x, y, (250, 250, 240)); put(im, x + 1, y, (250, 250, 240))
    outline(im, OUT)
    return im

def rock(ramp):
    im = new(32, 32)
    for (x, y, dx, dy) in ellipse_pts(16, 28, 9, 6):
        if dy < 0.6:
            put(im, x, y, ramp_pick(ramp, 0.2 + 0.8 * sphere_light(dx, dy), x, y))
    for (x, y, dx, dy) in ellipse_pts(22, 29, 4, 3):
        if dy < 0.6:
            put(im, x, y, ramp_pick(ramp, 0.1 + 0.8 * sphere_light(dx, dy), x, y))
    im[31:, :, 3] = 0
    outline(im, OUT)
    im[31, :, :] = 0
    return im

def pist_bush():
    im = new(32, 32)
    leaf = [(26, 70, 36), (40, 104, 44), (66, 140, 56), (104, 176, 70)]
    for (bx, by, r) in [(16, 24, 8), (10, 27, 6), (22, 27, 6)]:
        for (x, y, dx, dy) in ellipse_pts(bx, by, r, r * 0.85):
            put(im, x, y, ramp_pick(leaf, 0.15 + 0.85 * sphere_light(dx, dy) + (hsh(x // 2, y // 2, 4) - 0.5) * 0.3, x, y))
    for (x, y) in [(13, 21), (19, 23), (16, 26), (9, 26), (23, 26)]:
        put(im, x, y, (236, 200, 170)); put(im, x + 1, y, (190, 140, 120))
    im[31:, :, 3] = 0
    outline(im, OUT)
    return im

def crystal_cluster(cols):
    im = new(32, 32)
    for (x, h, w, lean) in [(16, 16, 3.5, 0), (11, 10, 2.5, -3), (21, 12, 2.5, 3), (7, 6, 2, -2), (25, 7, 2, 2)]:
        pts = [(x - w, 31), (x - w * 0.5 + lean * 0.4, 31 - h * 0.8), (x + lean, 31 - h), (x + w * 0.5 + lean * 0.4, 31 - h * 0.8), (x + w, 31)]
        poly_fill(im, pts, cols[1])
        poly_fill(im, [(x + lean, 31 - h), (x + w * 0.5 + lean * 0.4, 31 - h * 0.8), (x + w, 31), (x, 31)], cols[2])
        put(im, int(x + lean), 31 - h + 1, cols[3])
    outline(im, OUT)
    return im

def glow_mush():
    im = mushroom((80, 220, 230), spots=False)
    for (x, y) in [(13, 21), (18, 20), (20, 23)]:
        put(im, x, y, (230, 255, 255))
    return im

def alien_plant():
    im = new(32, 32)
    G = [(40, 20, 70), (90, 40, 140), (160, 80, 200)]
    for i in range(12):
        put(im, 16 + int(2 * math.sin(i * 0.5)), 31 - i, G[1])
    for (x, y) in [(18, 19), (14, 22)]:
        for (px_, py_, dx, dy) in ellipse_pts(x, y, 3, 2):
            put(im, px_, py_, G[2])
    rect(im, 15, 17, 3, 3, (255, 240, 120)); put(im, 16, 16, (255, 255, 220))
    outline(im, OUT)
    return im

def crate():
    im = new(32, 32)
    W_ = [(60, 50, 36), (96, 80, 56), (130, 110, 76), (170, 146, 100)]
    rect(im, 8, 16, 16, 16, W_[2])
    for i in range(16):
        put(im, 8 + i, 16 + i, W_[1]); put(im, 23 - i, 16 + i, W_[1])
    rect(im, 8, 16, 16, 2, W_[3]); rect(im, 8, 30, 16, 2, W_[0]); rect(im, 8, 16, 2, 16, W_[3]); rect(im, 22, 16, 2, 16, W_[0])
    outline(im, OUT); im[31:, :, :] = im[31:, :, :]
    return im

def barrel():
    im = new(32, 32)
    R = [(30, 70, 40), (50, 110, 60), (80, 160, 80), (140, 210, 120)]
    for y in range(14, 32):
        for x in range(9, 23):
            u = (x - 9) / 13
            put(im, x, y, ramp_pick(R, 0.2 + 0.75 * math.sin(u * math.pi) - (0.25 if u > 0.7 else 0), x, y))
    for y in (16, 23, 29):
        for x in range(9, 23): put(im, x, y, (40, 50, 50))
    rect(im, 13, 19, 6, 3, (240, 200, 40)); put(im, 15, 20, (40, 40, 30))
    outline(im, OUT)
    return im

def console():
    im = new(32, 32)
    M = [(30, 40, 40), (56, 70, 66), (90, 108, 100)]
    rect(im, 6, 18, 20, 14, M[1]); rect(im, 6, 18, 20, 2, M[2])
    rect(im, 9, 21, 14, 6, (10, 40, 24))
    rect(im, 10, 22, 8, 1, (90, 240, 130)); rect(im, 10, 24, 11, 1, (90, 240, 130))
    put(im, 9, 29, (255, 70, 70)); put(im, 12, 29, (255, 210, 70)); put(im, 15, 29, (90, 220, 120))
    outline(im, OUT)
    return im

def cone():
    im = new(32, 32)
    poly_fill(im, [(16, 18), (21, 30), (11, 30)], (240, 130, 40))
    for y in (22, 26):
        for x in range(10, 23):
            if im[y, x, 3]: put(im, x, y, (250, 250, 240))
    rect(im, 9, 30, 15, 2, (60, 60, 60))
    outline(im, OUT)
    return im

def lamp():
    im = new(32, 32)
    rect(im, 15, 12, 2, 20, (70, 84, 80)); rect(im, 15, 12, 1, 20, (130, 146, 136))
    rect(im, 12, 9, 8, 4, (90, 104, 100)); rect(im, 13, 12, 6, 2, (180, 255, 200))
    outline(im, OUT)
    return im

def build(outdir):
    rows = []
    park = [flower((236, 70, 80)), flower((255, 214, 70), 7), flower((250, 250, 250), 11), flower((170, 130, 250), 8),
            tuft(1, [(30, 80, 36), (56, 130, 50), (120, 190, 80)]), mushroom((220, 50, 50)), pist_bush(), rock([(80, 76, 82), (120, 116, 120), (164, 160, 158), (206, 202, 196)])]
    cosmo = [crystal_cluster([(20, 60, 90), (40, 150, 180), (120, 230, 240), (240, 255, 255)]),
             crystal_cluster([(80, 20, 80), (170, 50, 160), (240, 120, 220), (255, 220, 250)]),
             glow_mush(), alien_plant(), tuft(3, [(20, 60, 90), (30, 110, 140), (110, 220, 230)]),
             rock([(40, 26, 64), (66, 44, 100), (100, 72, 140), (150, 120, 190)]),
             crystal_cluster([(60, 60, 20), (170, 160, 40), (250, 240, 110), (255, 255, 220)]), glow_mush()]
    ship = [crate(), barrel(), console(), cone(), lamp(), crate(), barrel(), lamp()]
    save(sheet(park + cosmo + ship, 32, 32, 8), outdir + '/decor.png')

if __name__ == '__main__':
    import sys
    build(sys.argv[1])
