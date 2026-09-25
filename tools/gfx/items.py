import math
from px import *

OUT = (40, 26, 22)
SHELL = [(112, 78, 56), (160, 120, 84), (204, 166, 118), (230, 204, 158), (248, 234, 200)]
SHELL_IN = (252, 244, 222)
KERN = [(38, 84, 30), (70, 132, 44), (118, 180, 60), (168, 218, 92), (214, 244, 150)]
SKIN = (150, 86, 104)

def pistachio(img, cx, cy, rx, ry, spin=0.0, rot=0.0, open_=True, outline_c=OUT):
    """spin: angle around vertical axis (radians); rot: in-plane rotation."""
    layer = new(img.shape[1], img.shape[0])
    c = math.cos(spin)
    w = max(1.6, rx * abs(c))
    front = c > 0.15 and open_
    ca, sa = math.cos(rot), math.sin(rot)
    R = max(w, ry) + 2
    for y in range(int(cy - R), int(cy + R) + 1):
        for x in range(int(cx - R), int(cx + R) + 1):
            px_, py_ = x + 0.5 - cx, y + 0.5 - cy
            lx = px_ * ca + py_ * sa; ly = -px_ * sa + py_ * ca
            # slightly pointed at the top (almond)
            ryy = ry * (1.0 if ly > 0 else 1.0)
            wx = w * (1 - 0.18 * max(0, -ly / ry))
            dx, dy = lx / wx, ly / ryy
            d2 = dx * dx + dy * dy
            if d2 > 1: continue
            wdx = dx * ca - dy * sa; wdy = dx * sa + dy * ca
            t = 0.2 + 0.8 * sphere_light(wdx, wdy)
            col = ramp_pick(SHELL, t, x, y)
            if front:
                # opening lens, centred slightly right of middle
                ox = (lx - w * 0.12) / (w * 0.55)
                lens = abs(ox) < (1 - dy * dy) ** 0.8 and abs(dy) < 0.86
                if lens:
                    kx = ox; kt = 0.25 + 0.75 * sphere_light(kx * 0.8 * ca - dy * sa, kx * 0.8 * sa + dy * ca)
                    col = ramp_pick(KERN, kt, x, y)
                    if abs(ox) > 0.72 * (1 - dy * dy) ** 0.8: col = SKIN
            else:
                # seam line on the back / edge
                if abs(lx) < 0.6 and abs(dy) < 0.9 and c < -0.15: col = SHELL[1]
            put(layer, x, y, col)
    outline(layer, outline_c)
    blit_fast(img, layer, 0, 0)
    return img

def collectible_frames():
    frames = []
    for k in range(8):
        a = k * math.pi / 4
        im = new(24, 24)
        pistachio(im, 12, 12.5, 7.2, 9.6, spin=a, rot=0.18)
        # sparkle on facing frames
        if k in (0, 1):
            put(im, 7, 7, (255, 255, 240)); put(im, 8, 6, (255, 255, 240))
        frames.append(im)
    return frames

def lance_frames():
    fr = []
    for k in range(8):
        im = new(24, 24)
        pistachio(im, 12, 12, 5.2, 7.2, spin=0.0, rot=k * math.pi / 8)
        fr.append(im)
    return fr

def grenade_frames():
    fr = []
    for k in range(8):
        im = new(24, 24)
        rot = k * math.pi / 4
        pistachio(im, 12, 12.5, 7.0, 8.8, spin=math.pi, rot=rot, open_=False)
        ca, sa = math.cos(rot), math.sin(rot)
        # red band across the belly (perpendicular to long axis)
        for ti in range(-16, 17):
            t = ti * 0.5
            for ly, colr in ((-0.5, (230, 70, 44)), (0.5, (230, 70, 44)), (1.5, (150, 34, 26))):
                x = 12 + t * ca - ly * sa; y = 12.5 + t * sa + ly * ca
                xi, yi = int(math.floor(x)), int(math.floor(y))
                if get_a(im, xi, yi) and tuple(im[yi, xi, :3]) != OUT:
                    put(im, xi, yi, colr)
        # fuse cap + pin ring at the top of the long axis
        fx, fy = 12 + 9.6 * sa, 12.5 - 9.6 * ca
        for dx in (-1, 0, 1):
            for dy in (-1, 0):
                put(im, int(fx + dx), int(fy + dy), (86, 84, 96))
        put(im, int(fx), int(fy) - 1, (170, 170, 180))
        rx, ry = int(fx + 2), int(fy - 2)
        for (a_, b_) in [(0, 0), (1, 0), (1, 1), (0, 1)]:
            put(im, rx + a_, ry + b_ - 1, (200, 200, 60))
        outline(im, OUT)
        fr.append(im)
    return fr

def pellet_frames():
    fr = []
    for k in range(2):
        im = new(24, 24)
        shaded_ellipse(im, 12, 12, 6 if k == 0 else 5.5, 3.2, KERN, amb=0.35)
        rect(im, 12, 11, 3, 1, (240, 255, 200))
        outline(im, (30, 70, 24))
        fr.append(im)
    return fr

def mine_frames():
    fr = []
    for k in range(2):
        im = new(24, 24)
        shaded_ellipse(im, 12, 15, 8, 5.5, KERN, amb=0.3)
        pistachio(im, 12, 11, 4, 5.4, spin=0.0, rot=0.0)
        c = (255, 72, 60) if k == 0 else (120, 30, 30)
        rect(im, 11, 4, 2, 2, c)
        outline(im, OUT)
        fr.append(im)
    return fr

HEART = [
"..##...##..",
".####.####.",
"###########",
"###########",
"###########",
".#########.",
"..#######..",
"...#####...",
"....###....",
".....#.....",
]
def heart(full=True):
    im = new(24, 24)
    ramp = [(120, 20, 36), (186, 36, 52), (232, 64, 72), (255, 120, 120)] if full else [(40, 30, 40), (60, 48, 60), (80, 66, 80), (96, 84, 96)]
    for y, r in enumerate(HEART):
        for x, ch in enumerate(r):
            if ch == '#':
                dx = (x - 5) / 6.0; dy = (y - 4) / 5.5
                t = 0.25 + 0.75 * sphere_light(dx, dy)
                put(im, 6 + x, 7 + y, ramp_pick(ramp, t, x, y))
    if full:
        put(im, 8, 9, (255, 220, 220)); put(im, 9, 9, (255, 200, 200)); put(im, 8, 10, (255, 200, 200))
    outline(im, (30, 12, 20))
    return im

def pist_icon():
    im = new(24, 24)
    pistachio(im, 12, 12, 6.2, 8.4, spin=0.0, rot=0.3)
    return im

STAR = [
".....#.....",
"....###....",
"....###....",
"###########",
".#########.",
"..#######..",
"...#####...",
"..###.###..",
".##.....##.",
]
def star_icon():
    im = new(24, 24)
    ramp = [(190, 110, 20), (240, 170, 30), (255, 220, 70), (255, 250, 180)]
    for y, r in enumerate(STAR):
        for x, ch in enumerate(r):
            if ch == '#':
                t = 0.3 + 0.7 * sphere_light((x - 5) / 6, (y - 4) / 5)
                put(im, 6 + x, 7 + y, ramp_pick(ramp, t, x, y))
    outline(im, (60, 30, 10))
    return im

CLOCK = [
"...#####...",
"..#wwwww#..",
".#wwwkwww#.",
"#wwwwkwwww#",
"#wwwwkwwww#",
"#wwwwkkkww#",
"#wwwwwwwww#",
".#wwwwwww#.",
"..#wwwww#..",
"...#####...",
]
def clock_icon():
    im = from_ascii(CLOCK, {'#': (60, 70, 90), 'w': (236, 240, 244), 'k': (40, 40, 50)})
    out = new(24, 24); blit_fast(out, im, 6, 7); outline(out, (20, 20, 30)); return out

GUN = [
"......tTTt.....",
".....tTnnTt....",
"..EEEgGGGGgEZz.",
".EgGGGGGGGGgZYz",
".EggGGGGGGGgZZz",
"..EEEgEEEEEEEz.",
"...EzzE........",
"...Ezz.........",
]
GPAL = {'G': (168, 212, 88), 'g': (116, 170, 62), 'E': (72, 118, 44), 'T': (236, 214, 160), 't': (192, 160, 108),
        'n': (128, 200, 80), 'Z': (70, 64, 80), 'z': (40, 36, 48), 'Y': (246, 242, 234)}
def weapon_icons():
    lance = new(24, 24)
    # spear: brown shaft + pistachio tip
    for i in range(14):
        put(lance, 3 + i, 16 - i // 2, (120, 80, 50)); put(lance, 3 + i, 17 - i // 2, (84, 54, 34))
    pistachio(lance, 18, 9, 3.6, 5.6, rot=1.1)
    outline(lance, OUT)
    gun = new(24, 24); g = from_ascii(GUN, GPAL); blit_fast(gun, g, 4, 8); outline(gun, (24, 40, 20))
    gren = new(24, 24); blit_fast(gren, grenade_frames()[0], 0, 0)
    return [lance, gun, gren]

# ---------- power-up bubbles ----------
GLYPHS = {
 'shield': ["..######..", ".########.", "####oo####", "###oooo###", "####oo####", ".########.", ".########.", "..######..", "...####...", "....##...."],
 'triple': ["......###.", ".....####.", "......###.", "..........", "###..####.", "####.#####", "###..####.", "..........", "......###.", ".....####."],
 'rapid': [".....####.", "....####..", "...####...", "..####....", ".########.", "..######..", "....###...", "...###....", "..##......", ".#........"],
 'mega': ["#...##...#", ".#..##..#.", "..######..", ".###oo###.", "###oooo###", "###oooo###", ".###oo###.", "..######..", ".#..##..#.", "#...##...#"],
 'superJump': ["....##....", "...####...", "..######..", ".###..###.", "....##....", "...####...", "..######..", ".###..###.", "....##....", "....##...."],
 'magnet': [".ooo..ooo.", ".ooo..ooo.", ".###..###.", ".###..###.", ".###..###.", ".###..###.", ".########.", "..######..", "...####...", ".........."],
 'heart': ["..........", ".##....##.", "####..####", "##########", "##########", ".########.", "..######..", "...####...", "....##....", ".........."],
 'star': ["....##....", "....##....", "...####...", "##########", ".########.", "..######..", "..######..", ".###..###.", ".##....##.", ".........."],
 'turbo': ["..........", "##...##...", ".##...##..", "..##...##.", "...##...##", "...##...##", "..##...##.", ".##...##..", "##...##...", ".........."],
 'freeze': ["....##....", ".#..##..#.", "..#.##.#..", "...####...", "##########", "##########", "...####...", "..#.##.#..", ".#..##..#.", "....##...."],
 'ghost': ["..######..", ".########.", "##oo##oo##", "##oo##oo##", "##########", "##########", "##########", "##########", "#.##..##.#", ".........."],
 'ricochet': ["...#......", "..##......", ".########.", "..##....##", "...#.....#", ".........#", "........##", "..######..", "..........", ".........."],
 'tornado': ["##########", ".########.", "..######..", "...#####..", "....####..", "...####...", "..####....", "...###....", "....##....", ".....#...."],
 'double': ["..........", "#...#.###.", ".#.#.....#", "..#......#", ".#.#..###.", "#...#.#...", "......#...", "......####", "..........", ".........."],
 'hover': ["..........", "...####...", "..#oooo#..", "..######..", "##########", "o########o", ".########.", "..o.o.o...", "..........", ".........."],
 'seed': ["..##..##..", ".####.###.", ".####.##..", "..##.#....", "....##....", "....#.....", "....#.....", "..######..", ".oooooooo.", ".........."],
}
POWER_ORDER = ['shield', 'triple', 'rapid', 'mega', 'superJump', 'magnet', 'heart', 'star', 'turbo', 'freeze', 'ghost', 'ricochet', 'tornado', 'double', 'hover', 'seed']
POWER_COL = {'shield': '#4fc3f7', 'triple': '#ffca28', 'rapid': '#ff7043', 'mega': '#e040fb', 'superJump': '#69f0ae', 'magnet': '#b388ff',
             'heart': '#ef5350', 'star': '#ffd54f', 'turbo': '#00e5ff', 'freeze': '#81d4fa', 'ghost': '#ce93d8', 'ricochet': '#ffab40',
             'tornado': '#81c784', 'double': '#fff176', 'hover': '#80deea', 'seed': '#d4e157'}

def power_bubble(kind):
    im = new(24, 24)
    base = rgb(POWER_COL[kind])
    ramp = [mix(base, (0, 0, 0), 0.55), mix(base, (0, 0, 0), 0.3), base, mix(base, (255, 255, 255), 0.35), mix(base, (255, 255, 255), 0.7)]
    shaded_ellipse(im, 12, 12, 10.5, 10.5, ramp, amb=0.25)
    g = GLYPHS[kind]
    gl = new(24, 24)
    for y, r in enumerate(g):
        for x, ch in enumerate(r):
            if ch == '#': put(gl, 7 + x, 7 + y, (255, 255, 255))
            elif ch == 'o': put(gl, 7 + x, 7 + y, (60, 50, 70) if kind in ('ghost', 'mega') else (200, 200, 210))
    outline(gl, mix(base, (0, 0, 0), 0.7))
    blit_fast(im, gl, 0, 0)
    # glass highlight
    for (x, y) in [(6, 5), (7, 5), (5, 6), (5, 7), (8, 4), (9, 4)]:
        put(im, x, y, (255, 255, 255))
    outline(im, (26, 20, 34))
    return im

def build(outdir):
    cells = []
    cells += collectible_frames()                     # row 0
    cells += lance_frames()                           # row 1
    cells += grenade_frames()                         # row 2
    p = pellet_frames(); m = mine_frames()
    cells += [p[0], p[1], m[0], m[1], heart(True), heart(False), pist_icon(), star_icon()]  # row 3
    cells += weapon_icons() + [clock_icon(), None, None, None, None]                        # row 4
    cells += [power_bubble(k) for k in POWER_ORDER]   # rows 5-6
    img = sheet(cells, 24, 24, 8)
    save(img, outdir + '/items.png')
    return img

if __name__ == '__main__':
    import sys
    build(sys.argv[1] if len(sys.argv) > 1 else '.')
