"""Sousou HD sprite: same design/poses as build.py, rendered at 2.75x (cell 132x176) with a
more detailed face (eye whites + brown iris, thick brows, nose shading, lips, hair highlights).
Drawn in game at 0.5 world px per art px (-> 66x88 world cell, 1.375x the base sprite)."""
import math, json, os
from PIL import Image
import numpy as np
import build as B

S = 2.75
CW, CH = 132, 176
P = dict(B.P)
P['i'] = (128, 76, 40)    # iris light
P['I'] = (70, 40, 22)     # iris dark / pupil
P['l'] = (255, 255, 255)  # eye highlight
P['N'] = (206, 140, 106)  # nose shade
P['u'] = (232, 176, 140)  # lip top light
P['W'] = (150, 110, 84)   # hair highlight 2 (warm)
OUT = B.OUT

def upgrid(rows, s=S):
    """Smooth 'argmax' upscale of a char grid: every char becomes a soft mask resampled
    bicubically, then each HD pixel takes the strongest char -> clean curves, no jaggies."""
    h = len(rows); w = max(len(r) for r in rows)
    rows = [r.ljust(w, '.') for r in rows]
    chars = sorted(set(''.join(rows)))
    W, H = int(round(w * s)), int(round(h * s))
    stack = []
    for c in chars:
        m = np.array([[1.0 if ch == c else 0.0 for ch in r] for r in rows], np.float32)
        im = Image.fromarray((m * 255).astype(np.uint8), 'L').resize((W, H), Image.BICUBIC)
        stack.append(np.asarray(im, np.float32))
    idx = np.argmax(np.stack(stack), axis=0)
    return [''.join(chars[idx[y, x]] for x in range(W)) for y in range(H)]

def put(g, x, y, c):
    if 0 <= y < len(g) and 0 <= x < len(g[y]): g[y][x] = c

def hd_head(kind='normal'):
    base = [list(r.ljust(23, '.')) for r in B.HEAD]
    # erase 1x features (brows/eyes/mouth/blush/nose) -> plain skin, redraw in HD
    for y in range(9, 20):
        for x in range(9, 22):
            if base[y][x] in 'bweOMmrk' and not (x >= 20 or y >= 19 and x < 12):
                inside = any(base[y][xx] in 'sSk' for xx in range(x + 1, 23)) and any(base[y][xx] in 'sSk' for xx in range(0, x))
                if inside: base[y][x] = 'S' if base[y][x] != 'k' else 'S'
    g = [list(r) for r in upgrid([''.join(r) for r in base])]
    # hair highlights: soft strands (wavy) on the hair mass
    for (x0, y0, n, dx) in [(int(a * S / 2.5), int(b * S / 2.5), c, d) for (a, b, c, d) in ((14, 8, 9, 1), (20, 5, 7, 1), (9, 22, 12, 0), (6, 36, 10, 0), (27, 6, 5, 1))]:
        for i in range(n):
            xx = x0 + int(round(math.sin(i * 0.7) * 1.2)) + (i // 3 if dx else 0)
            yy = y0 + i
            if g[yy][xx] in 'hH': g[yy][xx] = 'L' if i % 3 else 'W'
    # lighter face centre (base grid was mostly mid-tone): S -> s away from edges
    SK = set('sSNr')
    H_, W_ = len(g), len(g[0])
    src = [r[:] for r in g]
    for y in range(H_):
        for x in range(W_):
            if src[y][x] != 'S': continue
            ok = True
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    if abs(dx) + abs(dy) > 5: continue
                    yy, xx = y + dy, x + dx
                    if not (0 <= yy < H_ and 0 <= xx < W_) or src[yy][xx] not in SK: ok = False; break
                if not ok: break
            if ok: g[y][x] = 's'
    # --- face in HD coords (head grid x*2.5) ---
    def eye(cx, top, closed=False, hurt=False, right=False):
        if hurt:
            pts = [(0, 0), (1, 1), (2, 2), (1, 3), (0, 4)]
            for (a, b) in pts:
                xx = cx + (a if not right else -a)
                put(g, xx, top + b, 'O'); put(g, xx + (1 if not right else -1), top + b, 'O')
            return
        if closed:
            for x in range(cx - 3, cx + 4): put(g, x, top + 3, 'O')
            for x in range(cx - 2, cx + 3): put(g, x, top + 4, 'k')
            return
        # upper lid (thick), white, iris 2x3 + pupil, highlight, lower lash hint
        for x in range(cx - 3, cx + 4): put(g, x, top, 'O')
        put(g, cx + 4, top + 1, 'O') if right else put(g, cx - 4, top + 1, 'O')
        for y in range(top + 1, top + 5):
            for x in range(cx - 3, cx + 4): put(g, x, y, 'w')
        for y in range(top + 1, top + 5):
            for x in (cx - 1, cx, cx + 1, cx + 2): put(g, x, y, 'i' if y >= top + 3 else 'I')
        for y in (top + 1, top + 2, top + 3): put(g, cx + 1, y, 'b'); put(g, cx, y, 'b')
        put(g, cx - 1, top + 4, 'I') if False else None
        put(g, cx + 2, top + 1, 'l'); put(g, cx - 1, top + 3, 'l')
        put(g, cx - 3, top + 4, 'S'); put(g, cx + 3, top + 4, 'S')
        for x in range(cx - 2, cx + 3): put(g, x, top + 5, 'k')
    Z = lambda v: int(round(v * S / 2.5))
    ey = Z(30)
    closed = kind == 'blink'; hurt = kind == 'hurt'
    eye(Z(31), ey, closed, hurt)
    eye(Z(44), ey, closed, hurt, right=True)
    # thick brows, slightly arched
    by0 = ey - 4
    for cx, w in ((Z(31), 4), (Z(44), 3)):
        for x in range(cx - w, cx + w + 1):
            put(g, x, by0 + (1 if x in (cx - w, cx + w) else 0), 'b')
            if cx - w < x < cx + w: put(g, x, by0 + 1, 'b')
        if hurt: put(g, cx - w + 1, by0 - 1, 'b'); put(g, cx + w - 1, by0 - 1, 'b')
    # nose: bridge shadow + nostril
    nx, ny = Z(38), Z(33)
    for (x, y, c) in [(0, 0, 'N'), (0, 1, 'N'), (0, 2, 'N'), (0, 3, 'N'), (1, 4, 'N'), (0, 5, 'k'), (1, 5, 'k'), (-1, 5, 'N'), (2, 5, 'S')]:
        put(g, nx + x, ny + y, c)
    # blush
    for (x, y) in [(Z(27), Z(38)), (Z(27) + 1, Z(38)), (Z(27) + 2, Z(38)), (Z(47), Z(38)), (Z(47) + 1, Z(38))]: put(g, x, y, 'r')
    mx, my = Z(38), Z(41)
    # mouth / lips
    if hurt:
        for (x, y, c) in [(-2, 0, 'O'), (-1, 0, 'O'), (0, 0, 'O'), (1, 0, 'O'), (-3, 1, 'O'), (-2, 1, 'M'), (-1, 1, 'm'), (0, 1, 'm'),
                          (1, 1, 'M'), (2, 1, 'O'), (-2, 2, 'O'), (-1, 2, 'O'), (0, 2, 'O'), (1, 2, 'O')]:
            put(g, mx + x, my + y, c)
    else:
        for (x, y, c) in [(-3, 0, 'k'), (-2, 0, 'M'), (-1, 0, 'M'), (0, 0, 'M'), (1, 0, 'M'), (2, 0, 'k'),
                          (-2, 1, 'm'), (-1, 1, 'm'), (0, 1, 'u'), (1, 1, 'm'), (-1, 2, 'k'), (0, 2, 'k')]:
            put(g, mx + x, my + y, c)
    return [''.join(r) for r in g]

HEADS = {k: hd_head(k) for k in ('normal', 'blink', 'hurt')}
TORSO = upgrid(B.TORSO); PELVIS = upgrid(B.PELVIS); SHOE = upgrid(B.SHOE)
BLASTER = upgrid(B.BLASTER); FLASH = upgrid(B.FLASH)

def blit(layer, rows, ox, oy, part, flip=False):
    ox = int(round(ox * S)); oy = int(round(oy * S))
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c in '. ': continue
            xx = ox + ((len(r) - 1 - x) if flip else x)
            layer.append(((xx, oy + y), P[c], part, c))

def capsule(p0, p1, w):
    return B.capsule((p0[0] * S, p0[1] * S), (p1[0] * S, p1[1] * S), w * S)

def limb_pts(pts, cols, part, out):
    light, base, shade = cols
    for xx, yy, sd, t in pts:
        c = light if sd > 0.45 else (shade if sd < -0.35 else base)
        out.append(((xx, yy), P[c], part, c))

polar = B.polar
def leg(out, hip, thigh, bend, part, back=False):
    knee = polar(hip, thigh, 6.5); ankle = polar(knee, thigh - bend, 6.5)
    cols = ('J', 'q', 'Q') if back else ('j', 'J', 'q')
    limb_pts(capsule(hip, knee, 4.6), cols, part, out)
    limb_pts(capsule(knee, ankle, 4.2), cols, part, out)
    ax, ay = int(round(ankle[0])), int(round(ankle[1]))
    shoe = [r.replace('R', 'X') for r in SHOE] if back else SHOE
    blit(out, shoe, ax - 2, ay - 1, part + '_shoe')
    return ankle

def arm(out, sh, up, bend, part, back=False, hand=True):
    elbow = polar(sh, up, 5.0); wrist = polar(elbow, up + bend, 4.5)
    skin = ('k', 'k', 'K') if back else ('s', 'S', 'k')
    shirt = ('C', 'C', 'D') if back else ('A', 'B', 'C')
    limb_pts(capsule(elbow, wrist, 3.0), skin, part, out)
    limb_pts(capsule(sh, elbow, 3.2), skin, part, out)
    slv_end = polar(sh, up, 3.0)
    limb_pts(capsule((sh[0], sh[1] - 0.5), slv_end, 5.0), shirt, part, out)
    if hand:
        hx, hy = polar(wrist, up + bend, 1.2)
        for xx, yy, sd, t in capsule((hx, hy), (hx, hy), 3.3):
            out.append(((xx, yy), P[skin[2] if sd < -0.5 else skin[0]], part, 'x'))
    return wrist

GRP = {'bleg': 'jeans', 'fleg': 'jeans', 'barm': 'skin', 'farm': 'skin', 'torso': 'shirt', 'pelvis': 'jeans', 'gun': 'gun'}
def render(pose):
    bx = pose.get('bx', 0); by = pose.get('by', 0); ly = pose.get('lean', 0)
    FL = pose['fleg']; BL = pose['bleg']
    def ext(th, bd):
        k = polar((0, 0), th, 6.5); a = polar(k, th - bd, 6.5); return a[1]
    hipY = pose.get('hipY')
    if hipY is None: hipY = 59 - max(ext(*FL), ext(*BL))
    hipY = int(round(hipY)) + by
    br = pose.get('br', 0)
    tx = 17 + bx; ty = hipY - 13 + br
    hx = tx - 6 + ly; hy = ty - 20
    L_bleg = []; leg(L_bleg, (tx + 6.0, hipY + 1.0), BL[0], BL[1], 'bleg', back=True)
    L_barm = []; arm(L_barm, (tx + 5.5, ty + 4.0), pose['barm'][0], pose['barm'][1], 'barm', back=True)
    L_torso = []; blit(L_torso, PELVIS, tx + 1, hipY - 1, 'pelvis'); blit(L_torso, TORSO, tx, ty, 'torso')
    L_fleg = []; leg(L_fleg, (tx + 7.5, hipY + 1.0), FL[0], FL[1], 'fleg')
    L_head = []; blit(L_head, HEADS[pose.get('face', 'normal')], hx, hy, 'head')
    sw = pose.get('sway', 0)
    if sw:
        hx2 = int(round(hx * S)); hy2 = int(round(hy * S))
        L_head = [((x + int(sw * S), y), c, p, ch) if (y - hy2 >= int(15 * S) and x - hx2 <= int(9 * S)) else ((x, y), c, p, ch) for ((x, y), c, p, ch) in L_head]
    L_farm = []
    wrist = arm(L_farm, (tx + pose.get('fsx', 8.5) + ly * 0.5, ty + 4.0), pose['farm'][0], pose['farm'][1], 'farm')
    L_gun = []
    if pose.get('gun'):
        gx, gy = int(round(wrist[0])) - 3, int(round(wrist[1])) - 4
        blit(L_gun, BLASTER, gx, gy, 'gun')
        if pose.get('flash'): blit(L_gun, FLASH, gx + 13, gy + 2, 'flash')
        wx, wy = wrist[0] * S, wrist[1] * S
        for xx, yy, sd, t in B.capsule((wx, wy + 1), (wx, wy + 1), 3.6 * S * 0.5 * 2):
            L_gun.append(((xx, yy), P['s' if sd > -0.3 else 'S'], 'fist', 's'))
    order = [L_bleg, L_barm, L_torso, L_fleg, L_head, L_farm, L_gun]
    img = {}
    for layer in order:
        mask = {}
        for (pos, col, part, ch) in layer: mask[pos] = (col, part, ch)
        ring = {}
        for pos, (col, part, ch) in mask.items():
            grp = part.split('_')[0]
            if grp in ('head', 'flash', 'fist'): continue
            x, y = pos
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)):
                q = (x + dx, y + dy)
                if q in mask or q not in img: continue
                if abs(dx) == 2 or abs(dy) == 2:
                    mid = (x + dx // 2, y + dy // 2)
                    if mid in mask: continue
                under = img[q][1].split('_')[0]
                if under == grp or img[q][2] in 'O': continue
                sel = GRP.get(grp, 'skin')
                if part.endswith('shoe'): sel = 'shoe'
                elif ch in 'ABCD': sel = 'shirt'
                if abs(dx) == 2 or abs(dy) == 2:
                    continue
                ring[q] = (B.SEL[sel], img[q][1], '#')
        img.update(ring)
        for pos, v in mask.items(): img[pos] = v
    arr = np.zeros((CH, CW, 4), np.uint8)
    for (x, y), (col, part, ch) in img.items():
        if 0 <= x < CW and 0 <= y < CH: arr[y, x, :3] = col; arr[y, x, 3] = 255
    # 2px global outline
    for it in range(2):
        a = arr[:, :, 3] > 0
        nb = np.zeros_like(a)
        nb[1:, :] |= a[:-1, :]; nb[:-1, :] |= a[1:, :]; nb[:, 1:] |= a[:, :-1]; nb[:, :-1] |= a[:, 1:]
        if it == 0:
            notout = a & ~((arr[:, :, 0] == OUT[0]) & (arr[:, :, 1] == OUT[1]) & (arr[:, :, 2] == OUT[2]))
            nb = np.zeros_like(a)
            nb[1:, :] |= notout[:-1, :]; nb[:-1, :] |= notout[1:, :]; nb[:, 1:] |= notout[:, :-1]; nb[:, :-1] |= notout[:, 1:]
        ol = nb & ~a
        arr[ol, :3] = OUT; arr[ol, 3] = 255
    return Image.fromarray(arr, 'RGBA')

def main(out_png):
    frames = [(n, render(p)) for n, p in B.FR]
    cols = 6; rows = math.ceil(len(frames) / cols)
    sheet = Image.new('RGBA', (cols * CW, rows * CH), (0, 0, 0, 0))
    for i, (n, im) in enumerate(frames):
        dy = CH - im.getbbox()[3]  # pieds sur la dernière ligne (comme le sprite de base)
        sheet.alpha_composite(im, ((i % cols) * CW, (i // cols) * CH + dy))
    sheet.save(out_png, optimize=True)
    return sheet

if __name__ == '__main__':
    import sys
    sh = main(sys.argv[1] if len(sys.argv) > 1 else 'sousou_sprite_hd.png')
    print('ok', sh.size)
