import math
from px import *

def poof_frames():
    """white/grey dust poof, 6 frames, 32x32"""
    fr = []
    ramp = [(120, 110, 130), (170, 164, 178), (214, 210, 220), (246, 244, 250)]
    puffs = [(-6, 2, 1.0), (6, 3, 0.9), (0, -5, 1.1), (-9, -4, 0.7), (9, -3, 0.75), (0, 7, 0.8)]
    for k in range(6):
        im = new(32, 32)
        t = k / 5.0
        spread = 2 + t * 9
        rad = 3.5 + t * 3.5 if k < 4 else 6.5 - (k - 3) * 2.0
        for i, (dx, dy, s) in enumerate(puffs):
            r = rad * s
            if r < 1: continue
            cx = 16 + dx * spread / 9; cy = 16 + dy * spread / 9 - t * 3
            shaded_ellipse(im, cx, cy, r, r, ramp, amb=0.35)
        if k >= 4:  # dissolve: punch holes
            for y in range(32):
                for x in range(32):
                    if hsh(x, y, k) < (0.35 if k == 4 else 0.65): im[y, x, 3] = 0
        if k < 4: outline(im, (70, 62, 80))
        fr.append(im)
    return fr

def burst_frames(core=(255, 255, 220), mid=(190, 240, 90), rim=(60, 130, 40)):
    """star-shaped impact burst, 5 frames"""
    fr = []
    for k in range(5):
        im = new(32, 32)
        R = [4, 8, 11, 12, 12][k]
        inner = [0, 0, 3, 7, 10][k]
        for y in range(32):
            for x in range(32):
                dx, dy = x + 0.5 - 16, y + 0.5 - 16
                d = math.hypot(dx, dy); a = math.atan2(dy, dx)
                spike = R * (0.55 + 0.45 * abs(math.cos(a * 4)))
                if inner <= d <= spike:
                    tt = d / max(spike, 1)
                    c = core if tt < 0.45 and k < 3 else (mid if tt < 0.8 else rim)
                    put(im, x, y, c)
        if k >= 3:
            for y in range(32):
                for x in range(32):
                    if hsh(x, y, 99 + k) < (0.3 if k == 3 else 0.6): im[y, x, 3] = 0
        fr.append(im)
    return fr

def muzzle_frames():
    fr = []
    for k in range(3):
        im = new(32, 32)
        L = [12, 15, 9][k]; H = [5, 6, 3][k]
        for y in range(32):
            for x in range(32):
                dx = x + 0.5 - 6; dy = y + 0.5 - 16
                if dx < 0: 
                    if dx * dx + dy * dy < (H + 1) ** 2 * 0.5: put(im, x, y, (255, 250, 200))
                    continue
                w = H * (1 - dx / L) if dx < L else -1
                if abs(dy) <= w:
                    c = (255, 255, 235) if abs(dy) < w * 0.4 else ((255, 230, 90) if abs(dy) < w * 0.75 else (160, 220, 70))
                    put(im, x, y, c)
        # side sparks
        if k < 2:
            for (sx, sy) in [(8, 10), (9, 22), (12, 9), (13, 23)]:
                put(im, sx + k, sy - k if sy < 16 else sy + k, (220, 255, 120))
        fr.append(im)
    return fr

def sparkle_frames():
    fr = []
    for k in range(4):
        im = new(32, 32)
        L = [2, 4, 6, 3][k]
        for i in range(-L, L + 1):
            c = (255, 255, 255) if abs(i) < 2 else (255, 240, 150)
            put(im, 16 + i, 16, c); put(im, 16, 16 + i, c)
        if k in (1, 2):
            for d in (1, 2):
                put(im, 16 + d, 16 + d, (255, 250, 200)); put(im, 16 - d, 16 - d, (255, 250, 200))
                put(im, 16 + d, 16 - d, (255, 250, 200)); put(im, 16 - d, 16 + d, (255, 250, 200))
        fr.append(im)
    return fr

def explosion_frames():
    """64x64 cartoony pistachio explosion, 7 frames"""
    fr = []
    fire = [(120, 30, 20), (200, 60, 30), (250, 130, 40), (255, 210, 80), (255, 250, 200)]
    smoke = [(50, 44, 56), (84, 76, 92), (120, 112, 128), (160, 152, 168)]
    blobs = [(0, 0, 1.0), (-10, 4, 0.8), (10, 5, 0.8), (-6, -9, 0.75), (8, -8, 0.8), (0, 10, 0.7), (-13, -3, 0.6), (13, -2, 0.6)]
    for k in range(7):
        im = new(64, 64)
        t = k / 6.0
        for i, (bx, by, s) in enumerate(blobs):
            grow = min(1.0, 0.35 + t * 1.6)
            r = (7 + 7 * grow) * s * (1.0 - max(0, t - 0.6) * 0.8)
            if r < 1.2: continue
            cx = 32 + bx * grow * 1.3; cy = 34 + by * grow * 1.3 - t * 8
            ramp = fire if k < 4 else smoke
            shaded_ellipse(im, cx, cy, r, r, ramp, amb=0.45 - t * 0.2, light=(-0.3, -0.8, 0.6))
        if k == 0:
            shaded_ellipse(im, 32, 34, 9, 9, [(255, 230, 120), (255, 255, 240)], amb=0.6)
        # flying pistachio shell bits / kernels
        if 1 <= k <= 5:
            for j in range(8):
                a = j * math.pi / 4 + 0.3
                d = 10 + k * 5
                x = int(32 + math.cos(a) * d); y = int(34 + math.sin(a) * d - k * 2 + k * k * 0.4)
                c = (150, 210, 80) if j % 2 else (230, 206, 160)
                rect(im, x, y, 2, 2, c)
        if k >= 5:
            for y in range(64):
                for x in range(64):
                    if hsh(x, y, 500 + k) < (0.3 if k == 5 else 0.6): im[y, x, 3] = 0
        else:
            outline(im, (40, 20, 20))
        fr.append(im)
    return fr

def build(outdir):
    cells = []
    cells += poof_frames() + [None, None]           # row0 (8 cols)
    cells += burst_frames() + [None] * 3              # row1 green impact
    cells += burst_frames((255, 255, 240), (255, 200, 90), (220, 90, 40)) + [None] * 3  # row2 orange impact (grenade/ricochet)
    cells += muzzle_frames() + sparkle_frames() + [None]  # row3
    save(sheet(cells, 32, 32, 8), outdir + '/fx.png')
    save(sheet(explosion_frames(), 64, 64, 7), outdir + '/boom.png')

if __name__ == '__main__':
    import sys
    build(sys.argv[1])
