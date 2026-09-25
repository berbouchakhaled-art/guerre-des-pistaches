"""Mobile UI pixel icons (touch buttons), rotate-phone prompt and app icons (deterministic)."""
import os
import numpy as np
from PIL import Image
from px import *
import items

INK = (22, 30, 18)
WHITE = (250, 248, 236)
SHADE = (190, 214, 150)

def glyph(rows, pal=None):
    pal = pal or {'#': WHITE, 's': SHADE, 'o': (120, 170, 60), 'y': (255, 214, 64), 'Y': (220, 160, 30), 'r': (230, 80, 60)}
    im = new(24, 24)
    h = len(rows); w = len(rows[0])
    ox = (24 - w) // 2; oy = (24 - h) // 2
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in pal: put(im, ox + x, oy + y, pal[ch])
    outline(im, INK)
    outline(im, INK)  # 2px chunky outline reads at small sizes
    return im

LEFT = ["......##....", ".....###....", "....####....", "...#########", "..##########", ".###########", ".sssssssssss", "..ssss######", "...sssssssss", "....ssss....", ".....sss....", "......ss...."]
def mirror(rows): return [r[::-1] for r in rows]
UP = ["....##....", "...####...", "..######..", ".########.", "##########", "sss####sss", "...####...", "...####...", "...ssss...", "...ssss..."]
DOWN = ["...####...", "...####...", "...####...", "...####...", "##########", ".########.", "..######..", "...ssss...", "....ss...."]
JUMP = ["....##....", "...####...", "..######..", ".########.", "##########", "...####...", "...####...", "..........", ".yy.yy.yy.", ".YY.YY.YY."]
MENU = ["##########", "ssssssssss", "..........", "##########", "ssssssssss", "..........", "##########", "ssssssssss"]
SND = ["....#.....", "...##..#..", "#####...#.", "#####.#.#.", "#####.#.#.", "#####...#.", "...##..#..", "....#....."]
MUTE = ["....#.....", "...##.....", "#####.r..r", "#####..rr.", "#####..rr.", "#####.r..r", "...##.....", "....#....."]
FULL = ["###....###", "##......##", "#.#....#.#", "..........", "..........", "#.#....#.#", "##......##", "###....###"]

def fire_icon():
    im = new(24, 24)
    items.pistachio(im, 13, 12, 5.2, 7.4, rot=1.2)
    for i, x in enumerate((2, 4, 6)):
        put(im, x, 11 + (i % 2), (255, 236, 150)); put(im, x + 1, 11 + (i % 2), (255, 236, 150))
    outline(im, INK)
    return im

def build_ui(outdir):
    w = items.weapon_icons()
    cells = [glyph(LEFT), glyph(mirror(LEFT)), glyph(UP), glyph(DOWN), glyph(JUMP), fire_icon(),
             glyph(MENU), glyph(SND), glyph(MUTE), glyph(FULL), w[0], w[1], w[2], None, None, None]
    save(sheet(cells, 24, 24, 16), outdir + '/ui.png')

def rotate_art(outdir):
    """64x48 landscape phone + curved arrow."""
    im = new(64, 48)
    # phone body (landscape)
    rect(im, 10, 14, 44, 26, (40, 52, 36))
    rect(im, 12, 16, 40, 22, (120, 200, 90))
    for y in range(16, 38):
        for x in range(12, 52):
            t = (y - 16) / 22.0
            put(im, x, y, ramp_pick([(150, 214, 100), (116, 180, 70), (84, 140, 50)], t, x, y))
    # tiny sousou-ish blob + ground on screen
    rect(im, 12, 34, 40, 4, (96, 64, 40)); rect(im, 12, 33, 40, 1, (150, 214, 100))
    rect(im, 20, 26, 4, 7, (240, 200, 160)); rect(im, 19, 24, 6, 4, (40, 30, 30))
    rect(im, 46, 26, 1, 3, (255, 236, 150)); rect(im, 30, 22, 3, 2, (200, 230, 120))
    rect(im, 53, 24, 1, 6, (70, 90, 60))
    outline(im, INK)
    save(im, outdir + '/rotate.png')

def app_icons(root):
    src = np.array(Image.open(os.path.join(root, 'assets', 'sousou-bg.png')).convert('RGBA'))[::9, ::9]  # 64x64 pixel portrait
    for size, name in ((180, 'apple-touch-icon.png'), (192, 'icon-192.png'), (512, 'icon-512.png')):
        cells = 80  # icon grid in art pixels
        im = new(cells, cells)
        for y in range(cells):
            for x in range(cells):
                t = y / cells
                put(im, x, y, ramp_pick([(196, 232, 128), (139, 195, 74), (85, 139, 47)], t, x, y))
        # pistachio corner accents
        for (cx, cy) in ((10, 10), (70, 70)):
            items.pistachio(im, cx, cy, 4.5, 6.5, rot=0.8)
        blit_fast(im, src, 8, 12)
        # frame
        for i in range(cells):
            for j in (0, 1): put(im, i, j, (61, 41, 20)); put(im, i, cells - 1 - j, (61, 41, 20)); put(im, j, i, (61, 41, 20)); put(im, cells - 1 - j, i, (61, 41, 20))
        img = Image.fromarray(im, 'RGBA').resize((size, size), Image.NEAREST).convert('RGB')
        img.save(os.path.join(root, 'assets', 'icons', name), optimize=True)

BTN = {
    # name: (fill, rim_top, rim_bottom)
    'green':     ((34, 64, 26, 115), (196, 228, 150, 215), (8, 18, 6, 150)),
    'green_on':  ((150, 204, 84, 215), (246, 255, 206, 240), (60, 100, 30, 220)),
    'jump':      ((250, 186, 40, 150), (255, 240, 170, 230), (140, 80, 10, 190)),
    'jump_on':   ((255, 222, 90, 230), (255, 252, 220, 250), (170, 110, 20, 230)),
    'fire':      ((110, 172, 56, 150), (220, 244, 180, 230), (30, 70, 18, 190)),
    'fire_on':   ((176, 224, 104, 230), (250, 255, 226, 250), (60, 110, 30, 230)),
    'dark':      ((12, 20, 10, 175), (150, 190, 120, 210), (0, 0, 0, 160)),
    'dark_on':   ((70, 110, 50, 220), (220, 250, 180, 240), (20, 40, 10, 200)),
}
def btn_slice(fill, rim, low, out=(16, 28, 12, 240)):
    """12x12 9-slice (slice 4) rounded pixel button."""
    n = 12
    im = new(n, n)
    def inside(x, y, inset):
        r = 3 - inset * 0.0
        lo, hi = inset, n - 1 - inset
        if x < lo or x > hi or y < lo or y > hi: return False
        # stepped corner cut
        cut = [3, 1, 1] if inset == 0 else [2, 1, 0]
        for k, c in enumerate(cut):
            if (y == lo + k or y == hi - k) and (x < lo + c or x > hi - c): return False
        return True
    for y in range(n):
        for x in range(n):
            if not inside(x, y, 0): continue
            if not inside(x, y, 1): put(im, x, y, out); continue
            c = fill
            if not inside(x, y - 1, 1) or (not inside(x - 1, y, 1) and y < 6): c = rim
            elif not inside(x, y + 1, 1) or not inside(x, y + 2, 1): c = low
            put(im, x, y, c)
    return im

def build_buttons(outdir):
    for name, (f, r, l) in BTN.items():
        save(btn_slice(f, r, l), outdir + '/btn_' + name + '.png')

def build(outdir):
    build_ui(outdir); rotate_art(outdir); build_buttons(outdir)
    root = os.path.abspath(os.path.join(outdir, '..', '..'))
    os.makedirs(os.path.join(root, 'assets', 'icons'), exist_ok=True)
    app_icons(root)
