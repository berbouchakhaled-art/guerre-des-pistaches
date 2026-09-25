import math
from px import *

T = 40
OUT = (26, 18, 22)

PAL = {
 'park': dict(
   dirt=[(52, 32, 26), (76, 48, 34), (102, 66, 44), (128, 86, 56), (152, 108, 70)],
   top=[(28, 68, 38), (44, 104, 44), (74, 146, 52), (116, 186, 64), (168, 220, 96)],
   stone=[(70, 66, 72), (110, 106, 110), (150, 146, 146), (196, 192, 186)],
 ),
 'cosmo': dict(
   dirt=[(22, 14, 42), (38, 24, 70), (58, 38, 102), (84, 58, 136), (116, 86, 168)],
   top=[(18, 56, 86), (26, 100, 130), (48, 160, 180), (110, 222, 222), (210, 255, 250)],
   stone=[(120, 40, 120), (190, 70, 170), (240, 130, 220), (255, 210, 250)],
 ),
 'ship': dict(
   dirt=[(20, 28, 28), (34, 48, 44), (52, 72, 64), (78, 102, 88), (112, 138, 116)],
   top=[(40, 40, 30), (240, 190, 40), (255, 222, 90)],
   stone=[(30, 60, 40), (60, 140, 70), (120, 220, 110), (210, 255, 190)],
 ),
}

def base_tex(world, x, y, seed):
    P = PAL[world]
    if world == 'park':
        n = fbm(x, y, seed, 14, 3)
        t = 0.25 + n * 0.55
        c = ramp_pick(P['dirt'], t, x, y)
        return c
    if world == 'cosmo':
        n = fbm(x, y, seed + 5, 12, 3)
        t = 0.2 + n * 0.6
        # strata bands
        t += 0.08 * math.sin((y + n * 10) * 0.45)
        return ramp_pick(P['dirt'], t, x, y)
    # ship: metal plate with brushed look
    n = vnoise(x * 3, y * 0.4, seed + 9, 6)
    t = 0.42 + n * 0.12
    return ramp_pick(P['dirt'], t, x, y)

def add_details(img, world, mask, seed):
    P = PAL[world]
    top = mask & 1
    y0 = 10 if top else 0
    if world == 'park':
        # pebbles
        for i in range(4):
            px_ = int(4 + hsh(i, seed, 1) * 32); py_ = int(y0 + 4 + hsh(i, seed, 2) * (34 - y0))
            if py_ > 37: continue
            rw = 2 + int(hsh(i, seed, 3) * 2)
            for (x, y, dx, dy) in ellipse_pts(px_, py_, rw, rw * 0.7):
                t = 0.2 + 0.8 * sphere_light(dx, dy)
                put(img, x, y, ramp_pick(P['stone'], t, x, y, False))
            put(img, px_ - rw, py_ + 1, P['dirt'][0])
        # tiny roots
        if hsh(seed, 7, 7) < 0.5:
            rx = int(6 + hsh(seed, 8, 8) * 28)
            for k in range(6):
                put(img, rx + (k % 3 == 2), y0 + 2 + k, P['dirt'][4] if k % 2 else P['dirt'][3])
    elif world == 'cosmo':
        # craters
        for i in range(2):
            cx = 6 + hsh(i, seed, 11) * 28; cy = y0 + 6 + hsh(i, seed, 12) * (26 - y0)
            r = 2.5 + hsh(i, seed, 13) * 2.5
            for (x, y, dx, dy) in ellipse_pts(cx, cy, r, r * 0.75):
                put(img, x, y, P['dirt'][1] if dy < 0.2 else P['dirt'][0])
            for (x, y, dx, dy) in ellipse_pts(cx, cy, r + 1, r * 0.75 + 1):
                if dx * dx + dy * dy > 0.75 and dy > 0.1: put(img, x, y, P['dirt'][3])
        # embedded pink crystal
        if hsh(seed, 3, 21) < 0.6:
            cx = int(8 + hsh(seed, 4, 22) * 24); cy = int(y0 + 10 + hsh(seed, 5, 23) * (22 - y0))
            pts = [(cx, cy - 4), (cx + 3, cy), (cx, cy + 4), (cx - 3, cy)]
            poly_fill(img, pts, P['stone'][1])
            poly_fill(img, [(cx, cy - 4), (cx + 3, cy), (cx, cy)], P['stone'][2])
            put(img, cx, cy - 2, P['stone'][3])
    else:
        # ship panels: seams, rivets, occasional light strip / vent
        for x in range(T):
            put(img, x, 20, P['dirt'][0]); put(img, x, 21, P['dirt'][3])
        for y in range(y0, T):
            put(img, 20, y, P['dirt'][0]); put(img, 21, y, P['dirt'][3])
        for (rx, ry) in [(4, y0 + 4), (35, y0 + 4), (4, 25), (35, 25), (16, 25), (25, y0 + 4)]:
            if ry < T - 2:
                put(img, rx, ry, P['dirt'][4]); put(img, rx + 1, ry + 1, P['dirt'][0]); put(img, rx + 1, ry, P['dirt'][2])
        k = hsh(seed, 1, 31)
        if k < 0.35:
            # green light strip
            for x in range(6, 16):
                put(img, x, 31, P['stone'][2]); put(img, x, 32, P['stone'][1])
            put(img, 6, 31, P['stone'][3])
        elif k < 0.6:
            # vent slots
            for i in range(4):
                for x in range(24, 35):
                    put(img, x, 27 + i * 3, P['dirt'][0]); put(img, x, 28 + i * 3, P['dirt'][3])

def top_layer(img, world, mask, seed):
    P = PAL[world]
    if world == 'park':
        for x in range(T):
            drip = int(hsh(x // 2, seed, 41) * 4) + (2 if hsh(x // 3, seed, 42) > 0.8 else 0)
            h = 7 + drip
            for y in range(h):
                if y == 0: c = P['top'][4]
                elif y == 1: c = P['top'][3]
                elif y < 4: c = ramp_pick(P['top'], 0.62, x, y)
                elif y < h - 1: c = ramp_pick(P['top'], 0.4 - (y - 4) * 0.04, x, y)
                else: c = P['top'][0]
                put(img, x, y, c)
            # soil shadow under grass
            put(img, x, h, P['dirt'][0]); put(img, x, h + 1, P['dirt'][1])
        # little light blades on the grass band
        for i in range(7):
            bx = int(2 + hsh(i, seed, 43) * 36)
            put(img, bx, 2, P['top'][4]); put(img, bx, 3, P['top'][3])
    elif world == 'cosmo':
        for x in range(T):
            h = 6 + int(hsh(x // 2, seed, 51) * 3)
            for y in range(h):
                c = P['top'][4] if y == 0 else (P['top'][3] if y == 1 else ramp_pick(P['top'], 0.55 - y * 0.05, x, y))
                if y == h - 1: c = P['top'][0]
                put(img, x, y, c)
            put(img, x, h, P['dirt'][0])
        # glowing specks
        for i in range(5):
            put(img, int(2 + hsh(i, seed, 52) * 36), 2 + int(hsh(i, seed, 53) * 3), (255, 255, 255))
    else:
        # hazard stripe band + bright lip
        for x in range(T):
            put(img, x, 0, (200, 214, 200)); put(img, x, 1, (150, 170, 150))
            for y in range(2, 8):
                stripe = ((x + y) // 5) % 2 == 0
                put(img, x, y, P['top'][1] if stripe else P['top'][0])
            put(img, x, 8, P['dirt'][0]); put(img, x, 9, P['dirt'][3])

def ground_tile(world, mask, seed):
    img = new(T, T)
    for y in range(T):
        for x in range(T):
            put(img, x, y, base_tex(world, x + seed * 40, y, seed))
    add_details(img, world, mask, seed)
    if mask & 1: top_layer(img, world, mask, seed)
    P = PAL[world]
    L, R, B, TP = mask & 4, mask & 8, mask & 2, mask & 1
    # edge shading (light from top-left)
    if L:
        for y in range(T):
            put(img, 1, y, P['dirt'][4] if not (TP and y < 9) else P['top'][-1]); put(img, 0, y, OUT)
    if R:
        for y in range(T):
            put(img, T - 2, y, P['dirt'][1] if not (TP and y < 9) else P['top'][1]); put(img, T - 1, y, OUT)
    if B:
        for x in range(T):
            put(img, x, T - 2, P['dirt'][0]); put(img, x, T - 1, OUT)
        if world == 'park':
            for i in range(3):
                rx = int(4 + hsh(i, seed, 61) * 32)
                for k in range(2 + int(hsh(i, seed, 62) * 3)):
                    put(img, rx, T - 2 - k, P['dirt'][3])
    if TP:
        for x in range(T): put(img, x, 0, OUT if world != 'park' else P['top'][4])
        if world == 'park':
            for x in range(T): put(img, x, 0, OUT)
            for x in range(T): put(img, x, 1, P['top'][4])
    # rounded corners
    def cut(x, y): img[y, x, 3] = 0
    if TP and L:
        cut(0, 0); cut(1, 0); cut(0, 1); put(img, 1, 1, OUT); put(img, 2, 1, OUT) if world == 'park' else None
        put(img, 2, 0, OUT); put(img, 0, 2, OUT)
    if TP and R:
        cut(T - 1, 0); cut(T - 2, 0); cut(T - 1, 1); put(img, T - 2, 1, OUT); put(img, T - 3, 0, OUT); put(img, T - 1, 2, OUT)
    if B and L:
        cut(0, T - 1); put(img, 1, T - 2, OUT); put(img, 0, T - 2, OUT); put(img, 1, T - 1, OUT)
    if B and R:
        cut(T - 1, T - 1); put(img, T - 2, T - 2, OUT); put(img, T - 1, T - 2, OUT); put(img, T - 2, T - 1, OUT)
    return img

# ---------------- other tiles ----------------
def brick(world):
    img = new(T, T)
    if world == 'park':
        ramp = [(92, 30, 26), (140, 50, 36), (182, 74, 48), (214, 110, 70), (236, 150, 100)]
        mortar = (60, 30, 30)
    elif world == 'cosmo':
        ramp = [(50, 20, 80), (84, 40, 130), (126, 70, 180), (170, 120, 220), (220, 180, 250)]
        mortar = (28, 12, 50)
    else:
        ramp = [(34, 44, 40), (58, 74, 64), (88, 108, 92), (124, 146, 124), (170, 190, 166)]
        mortar = (16, 22, 20)
    if world == 'ship':
        # supply crate with X brace
        for y in range(T):
            for x in range(T):
                put(img, x, y, ramp_pick(ramp, 0.45 + vnoise(x, y * 4, 3, 5) * 0.12, x, y))
        for i in range(T):
            for d in (-1, 0, 1):
                if 3 < i < T - 4:
                    put(img, i + d, i, ramp[1]); put(img, T - 1 - i + d, i, ramp[1])
            put(img, i, i - 1, ramp[3]) if 3 < i < T - 4 else None
        for k in range(4):
            for i in range(T):
                put(img, i, k, ramp[3] if k == 1 else ramp[1]); put(img, i, T - 1 - k, ramp[1] if k else ramp[0])
                put(img, k, i, ramp[3] if k == 1 else ramp[1]); put(img, T - 1 - k, i, ramp[1])
        rect(img, 16, 16, 8, 8, (240, 190, 40)); rect(img, 18, 18, 4, 4, (40, 40, 30))
    else:
        for y in range(T):
            row = y // 10
            off = 10 if row % 2 else 0
            for x in range(T):
                bx = (x + off) % 20
                by = y % 10
                if by == 9 or bx == 19:
                    put(img, x, y, mortar); continue
                t = 0.35 + 0.35 * (1 - by / 9) - 0.15 * (bx / 19) + (hsh((x + off) // 20, row, 5) - 0.5) * 0.2
                if by == 0 or bx == 0: t = 0.9
                put(img, x, y, ramp_pick(ramp, t, x, y))
        if world == 'cosmo':
            for (x, y) in [(6, 4), (27, 14), (12, 24), (31, 34)]:
                put(img, x, y, (255, 255, 255)); put(img, x + 1, y, ramp[4])
    for i in range(T):
        put(img, i, 0, OUT); put(img, i, T - 1, OUT); put(img, 0, i, OUT); put(img, T - 1, i, OUT)
    return img

QMARK = [
".####.",
"##..##",
"....##",
"...##.",
"..##..",
"..##..",
"......",
"..##..",
"..##..",
]
def qblock(world, f, used=False):
    img = new(T, T)
    if used:
        ramp = [(60, 44, 40), (90, 66, 56), (120, 90, 74), (150, 118, 96)]
    elif world == 'park':
        ramp = [(150, 80, 10), (214, 130, 20), (246, 180, 40), (255, 220, 100), (255, 248, 190)]
    elif world == 'cosmo':
        ramp = [(120, 60, 10), (200, 120, 30), (240, 176, 60), (255, 220, 120), (255, 250, 220)]
    else:
        ramp = [(40, 110, 50), (70, 170, 70), (120, 220, 90), (180, 250, 140), (240, 255, 220)]
    for y in range(T):
        for x in range(T):
            dx = (x - 19.5) / 22; dy = (y - 19.5) / 22
            t = 0.55 - dx * 0.25 - dy * 0.35
            put(img, x, y, ramp_pick(ramp, t, x, y))
    # bevel
    for i in range(T):
        put(img, i, 1, ramp[-1]); put(img, 1, i, ramp[-1]); put(img, i, T - 2, ramp[0]); put(img, T - 2, i, ramp[0])
        put(img, i, 0, OUT); put(img, i, T - 1, OUT); put(img, 0, i, OUT); put(img, T - 1, i, OUT)
    # rivets
    for (x, y) in [(4, 4), (34, 4), (4, 34), (34, 34)]:
        put(img, x, y, ramp[0]); put(img, x + 1, y, ramp[-1] if not used else ramp[1])
    if not used:
        # pistachio "?" glyph scaled x3
        for yy, r in enumerate(QMARK):
            for xx, ch in enumerate(r):
                if ch == '#':
                    for a in range(3):
                        for b in range(3):
                            X = 11 + xx * 3 + a; Y = 7 + yy * 3 + b
                            put(img, X + 1, Y + 1, ramp[0])
                            put(img, X, Y, (255, 255, 250) if a == 0 and b == 0 else (250, 244, 225))
        # shimmer sweep
        sx = [-10, 12, 34][f]
        for y in range(2, T - 2):
            for w in range(3):
                x = sx + y // 2 + w
                if 2 <= x < T - 2 and img[y, x, 3]:
                    c = img[y, x, :3]
                    put(img, x, y, mix(tuple(int(v) for v in c), (255, 255, 255), 0.5))
    return img

def platform(world, kind):
    """kind: single/L/M/R. visual slab occupies top ~18px"""
    img = new(T, T)
    P = PAL[world]
    if world == 'park':
        # floating grassy island chunk
        for x in range(T):
            left_in = kind in ('single', 'L'); right_in = kind in ('single', 'R')
            depth = 16
            if left_in and x < 8: depth = 10 + x // 1 - 2
            if right_in and x > T - 9: depth = 10 + (T - 1 - x) - 2
            depth = max(8, min(18, depth)) + int(hsh(x // 2, 3, 71) * 3)
            for y in range(depth):
                c = base_tex('park', x + 17, y + 5, 3)
                put(img, x, y, c)
            put(img, x, depth - 1, P['dirt'][0])
        tmp = new(T, T)
        for x in range(T):
            for y in range(6):
                c = P['top'][4] if y == 1 else (P['top'][3] if y == 2 else ramp_pick(P['top'], 0.5 - y * 0.06, x, y))
                if y == 5: c = P['top'][0]
                if img[y, x, 3]: put(img, x, y, c)
        for x in range(T):
            if img[0, x, 3]: put(img, x, 0, OUT)
        # hanging roots
        for i in range(3):
            rx = int(6 + hsh(i, 9, 72) * 28)
            ys = [y for y in range(T) if img[y, rx, 3]]
            if ys:
                for k in range(3 + int(hsh(i, 9, 73) * 3)):
                    put(img, rx + (k // 3), ys[-1] + 1 + k, P['dirt'][2])
    elif world == 'cosmo':
        # crystal slab
        cr = [(40, 20, 90), (80, 50, 160), (130, 100, 220), (190, 170, 250), (240, 230, 255)]
        for x in range(T):
            li = kind in ('single', 'L') and x < 6; ri = kind in ('single', 'R') and x > T - 7
            h = 14 if not (li or ri) else 9 + (x if li else T - 1 - x)
            h = min(h, 14)
            for y in range(h):
                t = 0.85 - y / 16 + (0.1 if (x // 6) % 2 else 0)
                put(img, x, y, ramp_pick(cr, t, x, y))
            # underside shards
            if not (li or ri):
                sh = int(3 + 4 * abs(math.sin(x * 0.7 + 1)))
                for y in range(h, h + sh - (abs((x % 8) - 4))):
                    put(img, x, y, cr[1] if y < h + 2 else cr[0])
        for x in range(T):
            put(img, x, 1, cr[4])
        outline_tile = True
    else:
        # hover pad: metal plate + thruster glow underside
        M = [(28, 36, 40), (50, 62, 66), (80, 96, 98), (120, 138, 136), (176, 192, 186)]
        for x in range(T):
            li = kind in ('single', 'L') and x < 3; ri = kind in ('single', 'R') and x > T - 4
            y0 = 1 if (li or ri) else 0
            for y in range(y0, 12):
                t = 0.7 - y / 15
                put(img, x, y, ramp_pick(M, t, x, y))
            put(img, x, 2, M[4]); put(img, x, 11, M[0])
        for (rx) in (5, 14, 25, 34):
            put(img, rx, 6, M[4]); put(img, rx + 1, 7, M[0])
        # thrusters
        for tx in ((8, 30) if kind == 'single' else ((12,) if kind in ('L', 'R') else (20,))):
            rect(img, tx - 3, 12, 7, 2, M[1])
            rect(img, tx - 2, 14, 5, 1, (140, 255, 170)); rect(img, tx - 1, 15, 3, 1, (80, 200, 120))
    # outline around opaque
    tmp = img.copy()
    ol = new(T, T)
    a = img[:, :, 3] > 0
    for y in range(T):
        for x in range(T):
            if a[y, x]:
                edge = False
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    X, Y = x + dx, y + dy
                    if 0 <= X < T and 0 <= Y < T:
                        if not a[Y, X]: edge = True
                    else:
                        if (dx == -1 and kind in ('single', 'L')) or (dx == 1 and kind in ('single', 'R')) or dy == -1: edge = True
                if edge: put(ol, x, y, OUT)
    blit_fast(img, ol, 0, 0)
    return img

def pipe(part):
    """5=top-left 6=top-right 7=body-left 8=body-right (pistachio-green pipe)"""
    img = new(T, T)
    G = [(20, 60, 30), (36, 100, 44), (60, 150, 60), (110, 200, 90), (180, 240, 150)]
    left = part in (5, 7)
    top = part in (5, 6)
    for y in range(T):
        for x in range(T):
            gx = x if left else x + T      # 0..79 across the pipe
            inset = 0 if top and y < 16 else 4
            if gx < inset or gx > 79 - inset: continue
            u = (gx - inset) / (79 - 2 * inset)
            t = 0.35 + 0.6 * math.sin(u * math.pi) ** 0.6 - (0.35 if u > 0.72 else 0) + (0.25 if 0.18 < u < 0.26 else 0)
            put(img, x, y, ramp_pick(G, t, x, y))
    if top:
        for x in range(T):
            put(img, x, 0, OUT); put(img, x, 1, G[4]); put(img, x, 15, OUT); put(img, x, 14, G[0])
    ol_x = 0 if left else T - 1
    for y in range(T):
        inset = 0 if top and y < 16 else 4
        X = inset if left else T - 1 - inset
        put(img, X, y, OUT)
    return img

def ice(kind):
    img = new(T, T)
    I = [(40, 90, 150), (80, 150, 210), (140, 206, 240), (200, 238, 255), (250, 255, 255)]
    for y in range(T):
        for x in range(T):
            t = 0.75 - y / 60 + 0.12 * math.sin((x - y) * 0.35) + (0.08 if hsh(x // 5, y // 5, 81) > 0.7 else 0)
            put(img, x, y, ramp_pick(I, t, x, y))
    # facet lines
    for k in range(3):
        x0 = int(6 + hsh(k, 1, 82) * 28)
        for i in range(12):
            put(img, x0 + i // 2, 8 + i + k * 6, I[4] if i % 3 else I[3])
    for x in range(T):
        put(img, x, 0, OUT); put(img, x, 1, I[4]); put(img, x, 2, I[4]); put(img, x, T - 1, OUT); put(img, x, T - 2, I[0])
    if kind in ('single', 'L'):
        for y in range(T): put(img, 0, y, OUT); put(img, 1, y, I[4])
    if kind in ('single', 'R'):
        for y in range(T): put(img, T - 1, y, OUT); put(img, T - 2, y, I[1])
    return img

def trampoline(world, f):
    img = new(T, T)
    M = [(30, 30, 40), (60, 60, 76), (100, 100, 120), (150, 150, 170)]
    pad = [(120, 20, 70), (190, 40, 110), (240, 90, 160), (255, 170, 210), (255, 230, 245)] if world == 'cosmo' else [(20, 90, 60), (40, 150, 90), (90, 210, 130), (160, 245, 180), (230, 255, 235)]
    comp = 2 if f else 0
    # base
    rect(img, 4, 30, 32, 8, M[1]); rect(img, 4, 30, 32, 2, M[3]); rect(img, 4, 37, 32, 1, M[0])
    # springs
    for sx in (10, 27):
        for i in range(10 - comp):
            y = 20 + comp + i
            put(img, sx + (i % 2) * 2, y, M[3]); put(img, sx + 1, y, M[2]); put(img, sx + 2 - (i % 2) * 2, y, M[1])
    # pad
    for (x, y, dx, dy) in ellipse_pts(20, 17 + comp, 17, 5):
        t = 0.2 + 0.8 * sphere_light(dx * 0.8, dy)
        put(img, x, y, ramp_pick(pad, t, x, y))
    for x in range(6, 34, 5):
        put(img, x, 16 + comp, pad[4])
    # arrows
    for (ax) in (14, 25):
        put(img, ax, 13 + comp, (255, 255, 255)); rect(img, ax - 1, 14 + comp, 3, 1, (255, 255, 255))
    ol = img.copy(); outline(ol, OUT); return ol

def lava(f, top):
    img = new(T, T)
    Lr = [(90, 10, 60), (170, 20, 80), (240, 60, 90), (255, 140, 80), (255, 230, 150)]
    for y in range(T):
        for x in range(T):
            n = fbm(x + f * 3, y - f * 2, 91, 10, 2)
            t = 0.35 + n * 0.45 - (y / 120 if not top else 0)
            put(img, x, y, ramp_pick(Lr, t, x, y))
    if top:
        for x in range(T):
            wave = int(2 + 2 * math.sin((x + f * 5) * 0.3))
            for y in range(wave): img[y, x, 3] = 0
            put(img, x, wave, Lr[4]); put(img, x, wave + 1, Lr[3])
        # bubbles
        bx = [(8, 12), (26, 18), (16, 26), (33, 9)][f]
        for (x, y, dx, dy) in ellipse_pts(bx[0], bx[1], 2.5, 2.5):
            put(img, x, y, Lr[4] if dy < 0 else Lr[3])
    return img

def build(outdir):
    for world in ('park', 'cosmo', 'ship'):
        cells = []
        for seed in (1, 2):
            for mask in range(16):
                cells.append(ground_tile(world, mask, seed + mask * 3))
        cells += [brick(world), qblock(world, 0), qblock(world, 1), qblock(world, 2), qblock(world, 0, True),
                  platform(world, 'single'), platform(world, 'L'), platform(world, 'M'), platform(world, 'R'),
                  pipe(5), pipe(6), pipe(7), pipe(8), ice('single'), ice('L'), ice('M')]
        cells += [ice('R'), trampoline(world, 0), trampoline(world, 1)] + [lava(f, True) for f in range(4)] + [lava(f, False) for f in range(4)] + [None] * 5
        save(sheet(cells, T, T, 16), outdir + '/tiles_%s.png' % world)

if __name__ == '__main__':
    import sys
    build(sys.argv[1])
