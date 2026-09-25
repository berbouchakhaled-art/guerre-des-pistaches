"""Sousou HD sprite = faithful 3x upscale of the approved 48x64 sheet (assets/sousou-sprite.png).
Scale3x (AdvMAME3x) keeps every shape, proportion and colour of the approved design and only
smooths the diagonals; then the face features are re-drawn at 3x resolution *at the same
place and size* (big brown eyes with a white catchlight, soft nose, small smile, soft blush).
Cell 144x192, sheet 864x576, same frame layout as the base sheet.  In game 1 art px =
1 canvas px (never a fractional scale) -> perfectly square, even pixels."""
import os, sys
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as B

F = 3
P = dict(B.P)
P['I'] = (40, 22, 16)      # pupil
P['i'] = (150, 92, 50)     # iris light (bottom glow)
P['l'] = (255, 255, 255)   # catchlight
P['u'] = (236, 176, 142)   # soft skin (between S and s) for anti-jaggy face details
P['p'] = (236, 172, 146)   # blush edge (between S and r)
P['x'] = (206, 142, 108)   # soft nose / smile shade (between S and k)
P['c'] = (120, 70, 44)     # soft lash end
P['v'] = (150, 110, 84)    # warm hair shine
RGB = {v: c for c, v in P.items()}


def scale3x(a):
    """AdvMAME3x on an RGBA uint8 array (exact colours, smoothed diagonals)."""
    h, w, _ = a.shape
    k = (a[:, :, 0].astype(np.int64) << 24) | (a[:, :, 1].astype(np.int64) << 16) | (a[:, :, 2].astype(np.int64) << 8) | a[:, :, 3]
    k[a[:, :, 3] == 0] = -1
    pk = np.pad(k, 1, mode='edge')
    pa = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode='edge')
    out = np.zeros((h * 3, w * 3, 4), np.uint8)
    for y in range(h):
        for x in range(w):
            A, Bb, C = pk[y, x], pk[y, x + 1], pk[y, x + 2]
            D, E, Fv = pk[y + 1, x], pk[y + 1, x + 1], pk[y + 1, x + 2]
            G, H, I = pk[y + 2, x], pk[y + 2, x + 1], pk[y + 2, x + 2]
            col = {A: pa[y, x], Bb: pa[y, x + 1], C: pa[y, x + 2], D: pa[y + 1, x], E: pa[y + 1, x + 1],
                   Fv: pa[y + 1, x + 2], G: pa[y + 2, x], H: pa[y + 2, x + 1], I: pa[y + 2, x + 2]}
            e = [E] * 9
            if Bb != H and D != Fv:
                db, bf, dh, hf = D == Bb, Bb == Fv, D == H, H == Fv
                e[0] = D if db else E
                e[1] = Bb if (db and E != C) or (bf and E != A) else E
                e[2] = Fv if bf else E
                e[3] = D if (db and E != G) or (dh and E != A) else E
                e[5] = Fv if (bf and E != I) or (hf and E != C) else E
                e[6] = D if dh else E
                e[7] = H if (dh and E != I) or (hf and E != G) else E
                e[8] = Fv if hf else E
            for i in range(9):
                out[y * 3 + i // 3, x * 3 + i % 3] = col[e[i]]
    return out


def ckey(px):
    return RGB.get(tuple(int(v) for v in px[:3]), '?') if px[3] else '.'


# ---- 3x face templates (columns/rows relative to the 3x cell of the base feature) ----
# eye: 9 wide x 7 tall, top-left = 3x of the base lid cell (lid row + eye row + 1 below)
EYE = [
    '.cOOOOOO.',
    'cOOOOOOOO',
    'wwellIIOO',
    'wweelIIeO',
    'wweIIIIeO',
    '.wweiiee.',
    '..uxxxu..',
]
EYE_R = [  # nearer eye (right), same design
    '.cOOOOOO.',
    'cOOOOOOOO',
    'wwellIIOO',
    'wweelIIeO',
    'wweIIIIeO',
    '.wweiiee.',
    '..uxxxu..',
]
BLINK = [
    '.........',
    '.........',
    '.........',
    'c.......c',
    'OO.....OO',
    '.OOOOOOO.',
    '..uxxxu..',
]
# brows: 12 (left) and 9 (right) px wide, relative to 3x of base brow cells
BROW_L = [
    '...bbbbbbbb.',
    '.bbbbbbbbbbb',
    'bbbbbbbbbbbc',
    'bbb.........',
]
BROW_R = [
    'bbbbbbb..',
    'bbbbbbbbb',
    'cbbbbbbbb',
    '.......bb',
]
NOSE = [
    '.x.....',
    '..x....',
    '..xx...',
    '...kkkx',
]
STRAND = [  # loose forehead lock (replaces the blocky 3x3 'd'/'k' dots), rel. (X0+9, Y0-12)
    'HHHHhddhH',
    'HHHhhddhH',
    'HHhhhdhhH',
    'sshhdhhss',
    'ssshdhsss',
    'sssshhsss',
    'sssssxsss',
    'sssssssss',
    'sssssssss',
]
MOUTH = [
    'x......x',
    '.xMMMMx.',
    '..MmmM..',
    '..mmmm..',
    '...uu...',
]
BLUSH_L = ['.pppp.', 'prrrrp', '.pppp.']
BLUSH_R = ['pp', 'rp', 'pp']


def stamp(out, rows, X, Y):
    for j, r in enumerate(rows):
        for i, c in enumerate(r):
            if c == '.':
                continue
            yy, xx = Y + j, X + i
            if 0 <= yy < out.shape[0] and 0 <= xx < out.shape[1]:
                out[yy, xx, :3] = P[c]
                out[yy, xx, 3] = 255


def refine_face(base, out, cx0, cy0, cw, ch):
    """base: 1x sheet array, out: 3x array. Cell origin cx0, cy0 (1x)."""
    cell = base[cy0:cy0 + ch, cx0:cx0 + cw]
    key = [[ckey(cell[y, x]) for x in range(cw)] for y in range(ch)]
    bs = [(x, y) for y in range(ch) for x in range(cw) if key[y][x] == 'b']
    if not bs:
        return 'nobrow'
    by = min(y for x, y in bs)
    bx = min(x for x, y in bs if y == by)
    kind = 'normal'
    if key[by + 3][bx] != 'w':
        kind = 'hurt' if 'O' in ''.join(key[by + 7][bx + 2:bx + 7]) else 'blink'
    X0, Y0 = (cx0 + bx) * F, (cy0 + by) * F
    stamp(out, STRAND, X0 + 9, Y0 - 12)
    if kind == 'hurt':
        return kind
    # 1) wipe the 1x features (and any Scale3x bleed) in the face box -> skin
    feat = set('bweOMmrk')
    for y in range(by, by + 8):
        for x in range(bx - 1, bx + 10):
            for j in range(F):
                for i in range(F):
                    yy, xx = (cy0 + y) * F + j, (cx0 + x) * F + i
                    if ckey(out[yy, xx]) in feat and not (x >= bx + 9 and key[y][x] == 'O'):
                        out[yy, xx, :3] = P['S']
    for x in (bx + 3, bx + 4):  # lower lip row
        for j in range(F):
            for i in range(F):
                yy, xx = (cy0 + by + 8) * F + j, (cx0 + x) * F + i
                if ckey(out[yy, xx]) in 'mM':
                    out[yy, xx, :3] = P['S']
    # 2) redraw at 3x, same positions/sizes as the approved 1x features
    stamp(out, BROW_L, X0, Y0 - 1)
    stamp(out, BROW_R, X0 + 6 * F, Y0 - 1)
    ey = Y0 + 2 * F
    if kind == 'blink':
        stamp(out, BLINK, X0, ey)
        stamp(out, BLINK, X0 + 5 * F, ey)
    else:
        stamp(out, EYE, X0, ey)
        stamp(out, EYE_R, X0 + 5 * F, ey)
    stamp(out, NOSE, X0 + 4 * F, Y0 + 4 * F)
    stamp(out, BLUSH_L, X0 - 1 * F, Y0 + 5 * F)
    stamp(out, BLUSH_R, X0 + 9 * F, Y0 + 5 * F)
    stamp(out, MOUTH, X0 + 3 * F - 1, Y0 + 7 * F)
    return kind


def main(out_png, src=None):
    src = src or os.path.join(HERE, '..', '..', 'assets', 'sousou-sprite.png')
    base = np.asarray(Image.open(src).convert('RGBA')).copy()
    base[base[:, :, 3] == 0] = 0
    out = scale3x(base)
    kinds = []
    for r in range(base.shape[0] // B.CH):
        for c in range(base.shape[1] // B.CW):
            kinds.append(refine_face(base, out, c * B.CW, r * B.CH, B.CW, B.CH))
    Image.fromarray(out, 'RGBA').save(out_png, optimize=True)
    return kinds


if __name__ == '__main__':
    print(main(sys.argv[1] if len(sys.argv) > 1 else 'sousou_sprite_hd.png', sys.argv[2] if len(sys.argv) > 2 else None))
