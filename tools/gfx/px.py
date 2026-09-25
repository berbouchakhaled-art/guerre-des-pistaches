"""Tiny deterministic pixel-art toolkit (numpy + Pillow). No randomness: all noise is hash based."""
import math
import numpy as np
from PIL import Image

def rgb(h):
    h = h.lstrip('#'); return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def new(w, h):
    return np.zeros((h, w, 4), np.uint8)

def save(img, path):
    Image.fromarray(img, 'RGBA').save(path, optimize=True)

def hsh(x, y, s=0):
    """deterministic hash -> [0,1)"""
    n = (int(x) * 374761393 + int(y) * 668265263 + int(s) * 2246822519) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFFFF) / float(0x1000000)

def vnoise(x, y, s=0, scale=16.0):
    fx, fy = x / scale, y / scale
    x0, y0 = math.floor(fx), math.floor(fy)
    tx, ty = fx - x0, fy - y0
    tx = tx * tx * (3 - 2 * tx); ty = ty * ty * (3 - 2 * ty)
    a = hsh(x0, y0, s); b = hsh(x0 + 1, y0, s); c = hsh(x0, y0 + 1, s); d = hsh(x0 + 1, y0 + 1, s)
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty

def fbm(x, y, s=0, scale=32.0, oct=4):
    v = 0; amp = 0.5; tot = 0
    for i in range(oct):
        v += vnoise(x, y, s + i * 17, scale) * amp; tot += amp
        amp *= 0.5; scale /= 2
    return v / tot

BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def dith(x, y):
    return (BAYER4[y & 3][x & 3] + 0.5) / 16.0

def ramp_pick(ramp, t, x=0, y=0, dither=True):
    """t in [0,1] -> colour from ramp with ordered dithering between steps"""
    t = max(0.0, min(0.9999, t))
    f = t * (len(ramp) - 1)
    i = int(f); fr = f - i
    if dither and i + 1 < len(ramp) and fr > dith(x, y):
        i += 1
    elif not dither and fr > 0.5 and i + 1 < len(ramp):
        i += 1
    return ramp[i]

def put(img, x, y, c, a=255):
    h, w = img.shape[:2]
    if 0 <= x < w and 0 <= y < h:
        if len(c) == 4: a = c[3]
        img[y, x, 0:3] = c[:3]; img[y, x, 3] = a

def get_a(img, x, y):
    h, w = img.shape[:2]
    if 0 <= x < w and 0 <= y < h: return img[y, x, 3]
    return 0

def rect(img, x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            put(img, xx, yy, c)

def ellipse_pts(cx, cy, rx, ry):
    pts = []
    for y in range(int(math.floor(cy - ry - 1)), int(math.ceil(cy + ry + 1)) + 1):
        for x in range(int(math.floor(cx - rx - 1)), int(math.ceil(cx + rx + 1)) + 1):
            dx = (x + 0.5 - cx) / max(rx, 0.01); dy = (y + 0.5 - cy) / max(ry, 0.01)
            if dx * dx + dy * dy <= 1.0:
                pts.append((x, y, dx, dy))
    return pts

LIGHT = (-0.55, -0.65, 0.52)
def sphere_light(dx, dy, light=LIGHT):
    d2 = dx * dx + dy * dy
    nz = math.sqrt(max(0.0, 1 - min(1.0, d2)))
    l = light; ln = math.sqrt(l[0]**2 + l[1]**2 + l[2]**2)
    return max(0.0, (dx * l[0] + dy * l[1] + nz * l[2]) / ln)

def shaded_ellipse(img, cx, cy, rx, ry, ramp, amb=0.18, rot=0.0, dither=True, light=LIGHT, mask=None):
    ca, sa = math.cos(rot), math.sin(rot)
    R = max(rx, ry) + 1
    for y in range(int(cy - R - 1), int(cy + R + 2)):
        for x in range(int(cx - R - 1), int(cx + R + 2)):
            px_, py_ = x + 0.5 - cx, y + 0.5 - cy
            lx = px_ * ca + py_ * sa; ly = -px_ * sa + py_ * ca
            dx, dy = lx / rx, ly / ry
            if dx * dx + dy * dy <= 1.0:
                if mask and not mask(x, y, dx, dy): continue
                # light in world space: rotate normal back
                wdx = dx * ca - dy * sa; wdy = dx * sa + dy * ca
                t = amb + (1 - amb) * sphere_light(wdx, wdy, light)
                put(img, x, y, ramp_pick(ramp, t, x, y, dither))

def poly_fill(img, pts, c):
    ys = [p[1] for p in pts]
    for y in range(int(min(ys)), int(max(ys)) + 1):
        yc = y + 0.5; xs = []
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
            if (y1 <= yc < y2) or (y2 <= yc < y1):
                xs.append(x1 + (yc - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(int(math.ceil(xs[i] - 0.5)), int(math.floor(xs[i + 1] - 0.5)) + 1):
                put(img, x, y, c)

def line(img, x0, y0, x1, y1, c):
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx = abs(x1 - x0); dy = -abs(y1 - y0); sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        put(img, x0, y0, c)
        if x0 == x1 and y0 == y1: break
        e2 = 2 * err
        if e2 >= dy: err += dy; x0 += sx
        if e2 <= dx: err += dx; y0 += sy

def outline(img, c, diag=False, only_alpha_above=0):
    a = img[:, :, 3] > only_alpha_above
    nb = np.zeros_like(a)
    nb[1:, :] |= a[:-1, :]; nb[:-1, :] |= a[1:, :]; nb[:, 1:] |= a[:, :-1]; nb[:, :-1] |= a[:, 1:]
    if diag:
        nb[1:, 1:] |= a[:-1, :-1]; nb[:-1, :-1] |= a[1:, 1:]; nb[1:, :-1] |= a[:-1, 1:]; nb[:-1, 1:] |= a[1:, :-1]
    o = nb & ~a
    img[o, 0:3] = c[:3]; img[o, 3] = 255
    return img

def inner_edge(img, c, side='all'):
    """recolour opaque pixels that border transparency (inner outline)."""
    a = img[:, :, 3] > 0
    tr = ~a
    e = np.zeros_like(a)
    e[1:, :] |= tr[:-1, :]; e[:-1, :] |= tr[1:, :]; e[:, 1:] |= tr[:, :-1]; e[:, :-1] |= tr[:, 1:]
    # borders of the image count as transparent
    e[0, :] = True; e[-1, :] = True; e[:, 0] = True; e[:, -1] = True
    m = e & a
    img[m, 0:3] = c[:3]
    return img

def blit(dst, src, ox, oy):
    h, w = src.shape[:2]
    for y in range(h):
        for x in range(w):
            if src[y, x, 3]:
                put(dst, ox + x, oy + y, tuple(int(v) for v in src[y, x, :3]), int(src[y, x, 3]))

def blit_fast(dst, src, ox, oy):
    """alpha-over composite (numpy)"""
    H, W = dst.shape[:2]; h, w = src.shape[:2]
    x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(W, ox + w), min(H, oy + h)
    if x0 >= x1 or y0 >= y1: return
    s = src[y0 - oy:y1 - oy, x0 - ox:x1 - ox].astype(np.float32)
    d = dst[y0:y1, x0:x1].astype(np.float32)
    sa = s[:, :, 3:4] / 255.0; da = d[:, :, 3:4] / 255.0
    oa = sa + da * (1 - sa)
    oc = np.where(oa > 0, (s[:, :, :3] * sa + d[:, :, :3] * da * (1 - sa)) / np.maximum(oa, 1e-6), 0)
    dst[y0:y1, x0:x1, :3] = np.clip(oc + 0.5, 0, 255).astype(np.uint8)
    dst[y0:y1, x0:x1, 3] = np.clip(oa[:, :, 0] * 255 + 0.5, 0, 255).astype(np.uint8)

def flip_h(img):
    return img[:, ::-1].copy()

def scale_nn(img, sx, sy=None):
    sy = sy or sx
    return np.repeat(np.repeat(img, sy, axis=0), sx, axis=1)

def resample(img, w, h):
    return np.array(Image.fromarray(img, 'RGBA').resize((w, h), Image.NEAREST))

def from_ascii(rows, pal):
    h = len(rows); w = max(len(r) for r in rows)
    img = new(w, h)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in pal: put(img, x, y, pal[ch])
    return img

def sheet(cells, cw, ch, cols):
    rows = (len(cells) + cols - 1) // cols
    out = new(cols * cw, rows * ch)
    for i, c in enumerate(cells):
        if c is None: continue
        blit_fast(out, c, (i % cols) * cw, (i // cols) * ch)
    return out

def mix(c1, c2, t):
    return tuple(int(round(c1[i] * (1 - t) + c2[i] * t)) for i in range(3))
