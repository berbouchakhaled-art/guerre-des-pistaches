#!/usr/bin/env python3
"""Homebrew NES original : Sousou, Le rayon.

NROM-128 (16 Ko PRG, 8 Ko CHR, mapper 0). Un seul ecran, le rayon.
Croix pour marcher (acceleration, freinage). A saute, et garde en l'air
sous une etiquette jaune pour s'y accrocher. B tenu court, B appuye tire
une pistache. Select donne un coup de fouet. Start lance.
Pas d'ennemis, pas de vies, pas de score. Les boites ne bougent pas.
"""

import os
import shutil
import subprocess
import zipfile

OUT = os.path.dirname(os.path.abspath(__file__))
ROM_NAME = "La guerre des pistaches"
NES_PATH = os.path.join(OUT, ROM_NAME + ".nes")
ZIP_PATH = os.path.join(OUT, ROM_NAME + ".zip")
STICK = "/Volumes/NO NAME"
STICK_ZIP = os.path.join(STICK, "001", ROM_NAME + ".zip")
FAV = os.path.join(STICK, "cubegm", "favorites.lst")

NMI_C, JOY, PREV = 0x10, 0x11, 0x12
STATE, LEVEL, LIVES = 0x13, 0x14, 0x15
WHIP, HANG, SWING = 0x16, 0x17, 0x19
FRAME = 0x18
PX, PY, VY = 0x20, 0x21, 0x22
RISING, GROUND, FACE = 0x23, 0x24, 0x25
VX = 0x29
INV, SCD, ANIM = 0x26, 0x27, 0x28
BON, BX, BY, BD = 0x30, 0x31, 0x32, 0x33
OAMI, IDX = 0x34, 0x35
ENT = 0x40
PTR, PALP = 0x90, 0x96
TMP, TMP2, TMP3 = 0x92, 0x93, 0x94
FLAG = ENT + 30
PLAT = ENT + 31
NUT = ENT + 18

NES_PAL = [
    (84, 84, 84), (0, 30, 116), (8, 16, 144), (48, 0, 136),
    (68, 0, 100), (92, 0, 48), (84, 4, 0), (60, 24, 0),
    (32, 42, 0), (8, 58, 0), (0, 64, 0), (0, 60, 0),
    (0, 50, 60), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (152, 150, 152), (8, 76, 196), (48, 50, 236), (92, 30, 228),
    (136, 20, 176), (160, 20, 100), (152, 34, 32), (120, 60, 0),
    (84, 90, 0), (40, 114, 0), (8, 124, 0), (0, 118, 40),
    (0, 102, 120), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (236, 238, 236), (76, 154, 236), (120, 124, 236), (176, 98, 236),
    (228, 84, 236), (236, 88, 180), (236, 106, 100), (212, 136, 32),
    (160, 170, 0), (116, 196, 0), (76, 208, 32), (56, 204, 108),
    (56, 180, 204), (60, 60, 60), (0, 0, 0), (0, 0, 0),
    (236, 238, 236), (168, 204, 236), (188, 188, 236), (212, 178, 236),
    (236, 174, 236), (236, 174, 212), (236, 180, 176), (228, 196, 144),
    (204, 210, 120), (180, 222, 120), (168, 226, 144), (152, 226, 180),
    (160, 214, 228), (160, 162, 160), (0, 0, 0), (0, 0, 0),
]


def pict(rows, cmap):
    lo, hi = [], []
    for r in rows:
        r = r.ljust(8, ".")[:8]
        b0 = b1 = 0
        for i, ch in enumerate(r):
            c = cmap.get(ch, 0)
            if c & 1:
                b0 |= 1 << (7 - i)
            if c & 2:
                b1 |= 1 << (7 - i)
        lo.append(b0)
        hi.append(b1)
    return bytes(lo[:8] + hi[:8])


def glyph(rows):
    return pict([r.ljust(8, ".") for r in rows], {"#": 3})


FONT = {
    "A": [" ## ", "#  #", "#  #", "####", "#  #", "#  #", "#  #"],
    "B": ["### ", "#  #", "#  #", "### ", "#  #", "#  #", "### "],
    "C": [" ###", "#   ", "#   ", "#   ", "#   ", "#   ", " ###"],
    "D": ["### ", "#  #", "#  #", "#  #", "#  #", "#  #", "### "],
    "E": ["####", "#   ", "#   ", "### ", "#   ", "#   ", "####"],
    "F": ["####", "#   ", "#   ", "### ", "#   ", "#   ", "#   "],
    "G": [" ###", "#   ", "#   ", "# ##", "#  #", "#  #", " ###"],
    "H": ["#  #", "#  #", "#  #", "####", "#  #", "#  #", "#  #"],
    "I": ["### ", " #  ", " #  ", " #  ", " #  ", " #  ", "### "],
    "J": ["  ##", "   #", "   #", "   #", "#  #", "#  #", " ## "],
    "K": ["#  #", "# # ", "##  ", "##  ", "# # ", "# # ", "#  #"],
    "L": ["#   ", "#   ", "#   ", "#   ", "#   ", "#   ", "####"],
    "M": ["#   #", "## ##", "# # #", "#   #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"],
    "O": [" ## ", "#  #", "#  #", "#  #", "#  #", "#  #", " ## "],
    "P": ["### ", "#  #", "#  #", "### ", "#   ", "#   ", "#   "],
    "R": ["### ", "#  #", "#  #", "### ", "# # ", "# # ", "#  #"],
    "S": [" ###", "#   ", "#   ", " ## ", "   #", "   #", "### "],
    "T": ["####", " #  ", " #  ", " #  ", " #  ", " #  ", " #  "],
    "U": ["#  #", "#  #", "#  #", "#  #", "#  #", "#  #", " ## "],
    "V": ["#  #", "#  #", "#  #", "#  #", "#  #", " ## ", " ## "],
    "W": ["#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"],
    "X": ["#  #", "#  #", " ## ", " ## ", " ## ", "#  #", "#  #"],
    "Y": ["#  #", "#  #", " ## ", " ## ", " ## ", " ## ", " ## "],
    "Z": ["####", "   #", "  # ", " #  ", "#   ", "#   ", "####"],
    "0": [" ## ", "#  #", "# ##", "# # #", "## #", "#  #", " ## "],
    "1": [" #  ", "##  ", " #  ", " #  ", " #  ", " #  ", "### "],
    "2": [" ## ", "#  #", "   #", "  # ", " #  ", "#   ", "####"],
    "3": ["### ", "   #", "   #", " ## ", "   #", "   #", "### "],
    "4": ["#  #", "#  #", "#  #", "####", "   #", "   #", "   #"],
    "5": ["####", "#   ", "#   ", "### ", "   #", "   #", "### "],
    "6": [" ## ", "#   ", "#   ", "### ", "#  #", "#  #", " ## "],
    "7": ["####", "   #", "  # ", "  # ", " #  ", " #  ", " #  "],
    "8": [" ## ", "#  #", "#  #", " ## ", "#  #", "#  #", " ## "],
    "9": [" ## ", "#  #", "#  #", " ###", "   #", "   #", " ## "],
}


def grass():
    lo, hi = [], []
    for r in range(8):
        if r < 2:
            lo.append(0xFF)
            hi.append(0x00)
        elif r == 2:
            lo.append(0xAA)
            hi.append(0x55)
        else:
            lo.append(0x00)
            hi.append(0xFF)
    return bytes(lo + hi)


def build_chr():
    bg = bytearray(4096)
    sp = bytearray(4096)

    def put(buf, i, tile):
        buf[i * 16:(i + 1) * 16] = tile

    wood = {"1": 1, "2": 2, "#": 3}
    put(bg, 1, pict([
        "11111111", "11111111", "########", "11111111",
        "11111111", "22222222", "11111111", "11111111",
    ], wood))
    put(bg, 2, pict([
        "11111111", "11211111", "11111111", "11112111",
        "11111111", "11111121", "11111111", "12111111",
    ], wood))
    put(bg, 3, pict([
        "########", "11111111", "11111111", "22222222",
        "11111111", "11111111", "11111111", "11111111",
    ], wood))
    box = {"#": 2, "1": 1, "E": 3}
    put(bg, 4, pict([
        "########", "#1111111", "#1111111", "#1111111",
        "#111EE11", "#111EE11", "#1111111", "#1111111",
    ], box))
    put(bg, 5, pict([
        "########", "1111111#", "1111111#", "1111111#",
        "11EE111#", "11EE111#", "1111111#", "1111111#",
    ], box))
    put(bg, 6, pict([
        "#1111111", "#1111111", "#1111111", "#1111111",
        "#1111111", "#1111111", "#1111111", "########",
    ], box))
    put(bg, 7, pict([
        "1111111#", "1111111#", "1111111#", "1111111#",
        "1111111#", "1111111#", "1111111#", "########",
    ], box))
    for ch, rows in FONT.items():
        padded = [r.ljust(8, ".")[:8] for r in rows]
        while len(padded) < 8:
            padded.append("........")
        if ch.isalpha():
            put(bg, 32 + ord(ch) - 65, glyph(padded))
        else:
            put(bg, 64 + ord(ch) - 48, glyph(padded))
    put(sp, 0, pict([
        ".HHH....", "HHHHH...", "HSSSSSH.", "HSSEESSH",
        ".SSMMS..", "........", "........", "........",
    ], {"H": 1, "S": 2, "E": 3, "M": 3}))
    put(sp, 1, pict([
        ".WWWW...", "WWWWWWW.", ".WWWWW..", ".BBBB...",
        ".BBBB...", ".RR.RR..", ".RR.RR..", "........",
    ], {"W": 1, "B": 2, "R": 3}))
    put(sp, 2, pict([
        ".WWWW...", "WWWWWWW.", ".WWWWW..", ".BBBB...",
        "BB..BB..", ".RR..RR.", "..R..R..", "........",
    ], {"W": 1, "B": 2, "R": 3}))
    put(sp, 5, pict([
        "..####..", ".#1111#.", "#11YY11#", ".#1111#.",
        "..####..", "........", "........", "........",
    ], {"#": 3, "1": 1, "Y": 2}))
    put(sp, 8, pict([
        "########", "#111111#", "#122221#", "#111111#",
        "########", "...##...", "........", "........",
    ], {"#": 3, "1": 1, "2": 2}))
    put(sp, 9, pict([
        "........", "........", "......##", "....##..",
        "..##....", "##......", "........", "........",
    ], {"#": 3}))
    put(sp, 10, pict([
        "..####..", ".######.", "##1111##", ".######.",
        "..####..", "........", "........", "........",
    ], {"#": 3, "1": 1}))
    return bytes(bg + sp)


def empty_nt():
    return bytearray(1024)


def text(buf, col, row, s):
    for i, ch in enumerate(s):
        if ch == " ":
            tile = 0
        elif "0" <= ch <= "9":
            tile = 64 + ord(ch) - 48
        elif "A" <= ch <= "Z":
            tile = 32 + ord(ch) - 65
        else:
            raise SystemExit("caractere hors police: " + ch)
        buf[row * 32 + col + i] = tile


def floor(buf):
    for row in range(25, 30):
        for col in range(32):
            buf[row * 32 + col] = 1


def plat_tiles(buf, x, y, w):
    row = y // 8
    col = x // 8
    for i in range(w // 8):
        buf[row * 32 + col + i] = 1


def flag_tiles(buf, x):
    col = x // 8
    buf[23 * 32 + col] = 4
    buf[24 * 32 + col] = 5


def fill_tiles(buf, col, row, w, h, tile):
    for y in range(row, row + h):
        for x in range(col, col + w):
            buf[y * 32 + x] = tile


def set_block(buf, tx, ty, pal):
    ax, ay = tx // 4, ty // 4
    quad = ((ty // 2) & 1) * 2 + ((tx // 2) & 1)
    shift = quad * 2
    i = 0x3C0 + ay * 8 + ax
    buf[i] = (buf[i] & ~(3 << shift)) | ((pal & 3) << shift)


def put_box(buf, col, row, pal):
    buf[row * 32 + col] = 4
    buf[row * 32 + col + 1] = 5
    buf[(row + 1) * 32 + col] = 6
    buf[(row + 1) * 32 + col + 1] = 7
    set_block(buf, col, row, pal)


def make_aisle():
    buf = empty_nt()
    text(buf, 13, 2, "RAYON")
    # Trois comptoirs : dessus, face avant jusqu'au sol, boites posees dessus.
    fill_tiles(buf, 2, 20, 9, 1, 3)
    fill_tiles(buf, 2, 21, 9, 4, 2)
    fill_tiles(buf, 13, 16, 10, 1, 3)
    fill_tiles(buf, 13, 17, 10, 8, 2)
    fill_tiles(buf, 23, 20, 8, 1, 3)
    fill_tiles(buf, 23, 21, 8, 4, 2)
    put_box(buf, 2, 18, 1)
    put_box(buf, 6, 18, 1)
    put_box(buf, 6, 16, 1)
    put_box(buf, 14, 14, 1)
    put_box(buf, 18, 14, 3)
    put_box(buf, 24, 18, 1)
    put_box(buf, 28, 18, 3)
    floor(buf)
    return bytes(buf)


def screen_text(lines):
    buf = empty_nt()
    floor(buf)
    for col, row, s in lines:
        text(buf, col, row, s)
    return bytes(buf)


# Dessus des comptoirs, puis le sol. y = surface, le sprite se pose a y-16.
RAYON_PLATS = [(16, 160, 72), (104, 128, 80), (184, 160, 64), (0, 200, 255)]
# Etiquettes jaunes : x, y du sprite. On s'y accroche en gardant A en l'air.
RAYON_TAGS = [(48, 176), (140, 144), (208, 176)]

AISLE_NT = make_aisle()
NTS = [AISLE_NT, AISLE_NT, AISLE_NT]
TITLE_NT = screen_text([
    (12, 4, "LE RAYON"),
    (13, 7, "SOUSOU"),
    (12, 11, "A SAUTE"),
    (11, 13, "ACCROCHE"),
    (8, 16, "B COURT ET TIRE"),
    (10, 18, "SELECT FOUET"),
    (13, 22, "START"),
])
WIN_NT = screen_text([(13, 8, "BRAVO"), (13, 11, "SOUSOU"), (13, 16, "START")])
OVER_NT = screen_text([(13, 10, "PERDU"), (13, 16, "START")])


def aisle_pal():
    bg = 0x30
    return bytes([
        bg, 0x17, 0x07, 0x0F,
        bg, 0x2A, 0x0A, 0x30,
        bg, 0x28, 0x0F, 0x30,
        bg, 0x23, 0x13, 0x30,
        bg, 0x07, 0x37, 0x0F,
        bg, 0x30, 0x12, 0x16,
        bg, 0x19, 0x28, 0x0F,
        bg, 0x28, 0x30, 0x0F,
    ])


PALS = [aisle_pal(), aisle_pal(), aisle_pal()]


def ent_bytes(enemies, nuts, flag, plats):
    raw = bytearray(43)
    o = 0
    for item in enemies:
        raw[o:o + 6] = bytes((item[0], item[1], item[2] & 255, item[3], item[4], item[5]))
        o += 6
    for x, y, alive in nuts:
        raw[o:o + 3] = bytes((x, y, alive))
        o += 3
    raw[o] = flag
    o += 1
    for x, y, w in plats:
        raw[o:o + 3] = bytes((x & 255, y, w & 255))
        o += 3
    if o != 43:
        raise SystemExit("entite %d" % o)
    return bytes(raw)


def rayon_ents():
    tags = [(x, y, 0, 0, 0, 0) for x, y in RAYON_TAGS]
    return ent_bytes(tags, [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)], 0, RAYON_PLATS)


ENTS = [rayon_ents(), rayon_ents(), rayon_ents()]


class Asm:
    def __init__(self):
        self.org = 0xC000
        self.buf = bytearray()
        self.labels = {}
        self.fixups = []

    def label(self, name):
        if name in self.labels:
            raise SystemExit("label en double " + name)
        self.labels[name] = self.org + len(self.buf)

    def b(self, *xs):
        for x in xs:
            self.buf.append(x & 255)

    def abs(self, op, addr=None, name=None):
        self.b(op)
        if name is not None:
            self.fixups.append((len(self.buf), name, "abs"))
            self.b(0, 0)
        else:
            self.b(addr & 255, (addr >> 8) & 255)

    def rel(self, op, name):
        self.b(op)
        self.fixups.append((len(self.buf), name, "rel"))
        self.b(0)

    def lo(self, name):
        self.fixups.append((len(self.buf), name, "lo"))
        self.b(0)

    def hi(self, name):
        self.fixups.append((len(self.buf), name, "hi"))
        self.b(0)

    def db(self, data):
        self.buf.extend(data)

    def lda_i(self, v): self.b(0xA9, v)
    def ldx_i(self, v): self.b(0xA2, v)
    def ldy_i(self, v): self.b(0xA0, v)
    def lda_z(self, a): self.b(0xA5, a)
    def sta_z(self, a): self.b(0x85, a)
    def stx_z(self, a): self.b(0x86, a)
    def ldx_z(self, a): self.b(0xA6, a)
    def lda_a(self, a): self.abs(0xAD, a)
    def sta_a(self, a): self.abs(0x8D, a)
    def stx_a(self, a): self.abs(0x8E, a)
    def sta_ax(self, a): self.abs(0x9D, a)
    def lda_ay(self, a): self.abs(0xB9, a)
    def sta_ay(self, a): self.abs(0x99, a)
    def adc_ay(self, a): self.abs(0x79, a)
    def cmp_ay(self, a): self.abs(0xD9, a)
    def sbc_ay(self, a): self.abs(0xF9, a)
    def lda_iy(self, a): self.b(0xB1, a)
    def lda_axn(self, name): self.abs(0xBD, name=name)
    def cmp_i(self, v): self.b(0xC9, v)
    def cmp_z(self, a): self.b(0xC5, a)
    def and_i(self, v): self.b(0x29, v)
    def adc_i(self, v): self.b(0x69, v)
    def adc_z(self, a): self.b(0x65, a)
    def sbc_i(self, v): self.b(0xE9, v)
    def sbc_z(self, a): self.b(0xE5, a)
    def inc_z(self, a): self.b(0xE6, a)
    def dec_z(self, a): self.b(0xC6, a)
    def cpx_i(self, v): self.b(0xE0, v)
    def cpy_i(self, v): self.b(0xC0, v)
    def bit_a(self, a): self.abs(0x2C, a)
    def jmp(self, n): self.abs(0x4C, name=n)
    def jsr(self, n): self.abs(0x20, name=n)
    def bne(self, n): self.rel(0xD0, n)
    def beq(self, n): self.rel(0xF0, n)
    def bcc(self, n): self.rel(0x90, n)
    def bcs(self, n): self.rel(0xB0, n)
    def bpl(self, n): self.rel(0x10, n)
    def asl(self): self.b(0x0A)
    def lsr(self): self.b(0x4A)
    def rol_z(self, a): self.b(0x26, a)
    def clc(self): self.b(0x18)
    def sec(self): self.b(0x38)
    def sei(self): self.b(0x78)
    def cld(self): self.b(0xD8)
    def pha(self): self.b(0x48)
    def pla(self): self.b(0x68)
    def tax(self): self.b(0xAA)
    def tay(self): self.b(0xA8)
    def txa(self): self.b(0x8A)
    def tya(self): self.b(0x98)
    def txs(self): self.b(0x9A)
    def inx(self): self.b(0xE8)
    def dex(self): self.b(0xCA)
    def iny(self): self.b(0xC8)
    def rts(self): self.b(0x60)
    def rti(self): self.b(0x40)

    def resolve(self):
        for pos, name, kind in self.fixups:
            if name not in self.labels:
                raise SystemExit("label manquant " + name)
            addr = self.labels[name]
            if kind == "abs":
                self.buf[pos] = addr & 255
                self.buf[pos + 1] = (addr >> 8) & 255
            elif kind == "lo":
                self.buf[pos] = addr & 255
            elif kind == "hi":
                self.buf[pos] = (addr >> 8) & 255
            else:
                src = self.org + pos + 1
                rel = addr - src
                if not -128 <= rel <= 127:
                    raise SystemExit("branche %s depuis $%04X ecart %d" % (name, src - 1, rel))
                self.buf[pos] = rel & 255

    def pad_vectors(self):
        target = 16384 - 6
        if len(self.buf) > target:
            raise SystemExit("PRG trop grand: %d" % len(self.buf))
        self.buf.extend(bytes(target - len(self.buf)))
        self.lo("nmi"); self.hi("nmi")
        self.lo("reset"); self.hi("reset")
        self.lo("irq"); self.hi("irq")


def program():
    a = Asm()

    a.label("nmi")
    a.pha(); a.txa(); a.pha(); a.tya(); a.pha()
    a.inc_z(NMI_C)
    a.lda_i(2); a.sta_a(0x4014)
    a.lda_i(0); a.sta_a(0x2005); a.sta_a(0x2005)
    a.pla(); a.tay(); a.pla(); a.tax(); a.pla(); a.rti()

    a.label("irq")
    a.rti()

    a.label("wait_nmi")
    a.lda_z(NMI_C)
    a.label("wait_loop")
    a.cmp_z(NMI_C)
    a.beq("wait_loop")
    a.rts()

    a.label("read_joy")
    a.lda_i(1); a.sta_a(0x4016)
    a.lda_i(0); a.sta_a(0x4016)
    a.ldx_i(8)
    a.label("joy_loop")
    a.lda_a(0x4016); a.lsr(); a.rol_z(JOY)
    a.dex(); a.bne("joy_loop")
    a.rts()

    def edge(name, mask):
        a.label(name)
        a.lda_z(PREV); a.and_i(mask); a.bne(name + "_no")
        a.lda_z(JOY); a.and_i(mask); a.beq(name + "_no")
        a.sec(); a.rts()
        a.label(name + "_no")
        a.clc(); a.rts()

    edge("start_edge", 0x10)
    edge("a_edge", 0x80)
    edge("b_edge", 0x40)
    edge("select_edge", 0x20)

    a.label("beep")
    a.lda_i(0x0E); a.sta_a(0x4000)
    a.lda_i(0); a.sta_a(0x4001)
    a.lda_i(0xA0); a.sta_a(0x4002)
    a.lda_i(0x20); a.sta_a(0x4003)
    a.rts()

    a.label("blip")
    a.lda_i(0x0E); a.sta_a(0x400C)
    a.lda_i(0x04); a.sta_a(0x400E)
    a.lda_i(0x18); a.sta_a(0x400F)
    a.rts()

    a.label("copy32")
    a.ldy_i(0)
    a.label("c32")
    a.lda_iy(PALP); a.sta_a(0x2007)
    a.iny(); a.cpy_i(32); a.bne("c32")
    a.rts()

    a.label("copy1024")
    a.ldx_i(4)
    a.label("c4_page")
    a.ldy_i(0)
    a.label("c4_byte")
    a.lda_iy(PTR); a.sta_a(0x2007)
    a.iny(); a.bne("c4_byte")
    a.inc_z(PTR + 1)
    a.dex(); a.bne("c4_page")
    a.rts()

    a.label("show_screen")
    a.lda_i(0); a.sta_a(0x2000); a.sta_a(0x2001)
    a.lda_i(0x3F); a.sta_a(0x2006)
    a.lda_i(0x00); a.sta_a(0x2006)
    a.jsr("copy32")
    a.lda_i(0x20); a.sta_a(0x2006)
    a.lda_i(0x00); a.sta_a(0x2006)
    a.jsr("copy1024")
    a.lda_i(0); a.sta_a(0x2005); a.sta_a(0x2005)
    a.lda_i(0x88); a.sta_a(0x2000)
    a.lda_i(0x1E); a.sta_a(0x2001)
    a.rts()

    a.label("copy_ent")
    a.ldy_i(0)
    a.label("ce_loop")
    a.lda_iy(PTR); a.sta_ay(ENT)
    a.iny(); a.cpy_i(43); a.bne("ce_loop")
    a.rts()

    a.label("begin_level")
    a.lda_i(1); a.sta_z(STATE)
    a.lda_i(24); a.sta_z(PX)
    a.lda_i(184); a.sta_z(PY)
    a.lda_i(0)
    a.sta_z(VY); a.sta_z(RISING); a.sta_z(BON); a.sta_z(SCD); a.sta_z(ANIM); a.sta_z(VX)
    a.sta_z(HANG); a.sta_z(WHIP); a.sta_z(SWING)
    a.lda_i(1); a.sta_z(GROUND); a.sta_z(FACE)
    a.lda_i(90); a.sta_z(INV)
    a.ldx_z(LEVEL)
    a.lda_axn("ent_lo"); a.sta_z(PTR)
    a.lda_axn("ent_hi"); a.sta_z(PTR + 1)
    a.jsr("copy_ent")
    a.ldx_z(LEVEL)
    a.lda_axn("pal_lo"); a.sta_z(PALP)
    a.lda_axn("pal_hi"); a.sta_z(PALP + 1)
    a.lda_axn("nt_lo"); a.sta_z(PTR)
    a.lda_axn("nt_hi"); a.sta_z(PTR + 1)
    a.jsr("show_screen")
    a.rts()

    a.label("new_game")
    a.lda_i(0); a.sta_z(LEVEL)
    a.lda_i(3); a.sta_z(LIVES)
    a.jsr("begin_level")
    a.rts()

    def load_pair(name, nt_name):
        a.label(name)
        a.b(0xA9); a.lo("pal0"); a.sta_z(PALP)
        a.b(0xA9); a.hi("pal0"); a.sta_z(PALP + 1)
        a.b(0xA9); a.lo(nt_name); a.sta_z(PTR)
        a.b(0xA9); a.hi(nt_name); a.sta_z(PTR + 1)
        a.rts()

    a.label("go_title")
    a.lda_i(0); a.sta_z(STATE)
    a.jsr("load_title_ptrs"); a.jsr("show_screen"); a.rts()

    a.label("go_win")
    a.lda_i(4); a.sta_z(STATE)
    a.jsr("load_win_ptrs"); a.jsr("show_screen"); a.rts()

    a.label("go_over")
    a.lda_i(3); a.sta_z(STATE)
    a.jsr("load_over_ptrs"); a.jsr("show_screen"); a.rts()

    load_pair("load_title_ptrs", "title_nt")
    load_pair("load_win_ptrs", "win_nt")
    load_pair("load_over_ptrs", "over_nt")

    a.label("move_player")
    a.inc_z(ANIM)
    a.jsr("hang_control"); a.bcc("do_move"); a.jmp("player_actions")
    a.label("do_move")
    # Marche 2 px, course 4 px si B est tenu (comme le bouton course de Mario).
    a.lda_i(2); a.sta_z(TMP)
    a.lda_z(JOY); a.and_i(0x40); a.beq("spd_walk")
    a.lda_i(4); a.sta_z(TMP)
    a.label("spd_walk")
    a.lda_z(JOY); a.and_i(0x01); a.beq("try_left")
    a.lda_z(JOY); a.and_i(0x02); a.bne("coast")
    a.lda_z(FACE); a.bne("accel_right")
    a.lda_z(VX); a.beq("face_to_right")
    a.dec_z(VX); a.jmp("apply_x")
    a.label("face_to_right")
    a.lda_i(1); a.sta_z(FACE)
    a.label("accel_right")
    a.lda_z(VX); a.cmp_z(TMP); a.bcs("apply_x")
    a.inc_z(VX); a.jmp("apply_x")
    a.label("try_left")
    a.lda_z(JOY); a.and_i(0x02); a.beq("coast")
    a.lda_z(FACE); a.beq("accel_left")
    a.lda_z(VX); a.beq("face_to_left")
    a.dec_z(VX); a.jmp("apply_x")
    a.label("face_to_left")
    a.lda_i(0); a.sta_z(FACE)
    a.label("accel_left")
    a.lda_z(VX); a.cmp_z(TMP); a.bcs("apply_x")
    a.inc_z(VX); a.jmp("apply_x")
    a.label("coast")
    a.lda_z(VX); a.beq("apply_x")
    a.dec_z(VX)
    a.label("apply_x")
    a.lda_z(VX); a.beq("no_move_x")
    a.lda_z(FACE); a.beq("apply_left")
    a.lda_z(PX); a.clc(); a.adc_z(VX); a.cmp_i(233); a.bcc("store_right")
    a.lda_i(232)
    a.label("store_right")
    a.sta_z(PX); a.jmp("no_move_x")
    a.label("apply_left")
    a.lda_z(PX); a.sec(); a.sbc_z(VX); a.cmp_i(8); a.bcs("store_left")
    a.lda_i(8)
    a.label("store_left")
    a.sta_z(PX)
    a.label("no_move_x")
    a.lda_z(RISING); a.beq("do_fall")
    # Relacher A coupe le saut : petit bond si on tapote, grand saut si on garde A.
    a.lda_z(JOY); a.and_i(0x80); a.bne("rise_full")
    a.lda_z(VY); a.cmp_i(6); a.bcc("rise_full")
    a.lda_i(5); a.sta_z(VY)
    a.label("rise_full")
    a.lda_z(PY); a.sec(); a.sbc_z(VY); a.sta_z(PY)
    a.lda_z(VY); a.beq("rise_end")
    a.dec_z(VY); a.jmp("vert_done")
    a.label("rise_end")
    a.lda_i(0); a.sta_z(RISING); a.jmp("vert_done")
    a.label("do_fall")
    a.jsr("land_check")
    a.lda_z(GROUND); a.bne("vert_done")
    a.lda_z(VY); a.cmp_i(4); a.bcs("no_grav")
    a.inc_z(VY)
    a.label("no_grav")
    a.lda_z(PY); a.clc(); a.adc_z(VY); a.sta_z(PY)
    a.label("vert_done")
    a.lda_z(PY); a.cmp_i(40); a.bcs("no_ceil")
    a.lda_i(40); a.sta_z(PY)
    a.lda_i(0); a.sta_z(RISING); a.sta_z(VY)
    a.label("no_ceil")
    a.jsr("a_edge"); a.bcc("no_jump")
    a.lda_z(GROUND); a.beq("no_jump")
    a.lda_i(1); a.sta_z(RISING)
    a.lda_i(9); a.sta_z(VY)
    a.lda_i(0); a.sta_z(GROUND)
    a.jsr("beep")
    a.label("no_jump")
    a.jsr("try_grab")
    a.label("player_actions")
    a.lda_z(BON); a.bne("no_shot")
    a.lda_z(SCD); a.bne("no_shot")
    a.jsr("b_edge"); a.bcc("no_shot")
    a.lda_i(1); a.sta_z(BON)
    a.lda_z(PY); a.clc(); a.adc_i(4); a.sta_z(BY)
    a.lda_z(FACE); a.sta_z(BD); a.beq("shot_left")
    a.lda_z(PX); a.clc(); a.adc_i(14); a.sta_z(BX); a.jmp("shot_ok")
    a.label("shot_left")
    a.lda_z(PX); a.sec(); a.sbc_i(4); a.sta_z(BX)
    a.label("shot_ok")
    a.lda_i(10); a.sta_z(SCD)
    a.jsr("blip")
    a.label("no_shot")
    a.jsr("whip_tick")
    a.lda_z(SCD); a.beq("no_scd"); a.dec_z(SCD)
    a.label("no_scd")
    a.lda_z(INV); a.beq("no_inv"); a.dec_z(INV)
    a.label("no_inv")
    a.rts()

    a.label("land_check")
    a.lda_i(0); a.sta_z(GROUND)
    a.lda_z(RISING); a.bne("land_out")
    a.ldx_i(0)
    a.label("land_lp")
    a.txa(); a.sta_z(TMP); a.asl(); a.clc(); a.adc_z(TMP); a.tay()
    a.lda_ay(PLAT + 2); a.beq("land_nx"); a.sta_z(TMP3)
    a.lda_ay(PLAT); a.sta_z(TMP)
    a.lda_ay(PLAT + 1); a.sta_z(TMP2)
    a.lda_z(PX); a.clc(); a.adc_i(14); a.cmp_z(TMP); a.bcc("land_nx")
    a.lda_z(TMP); a.clc(); a.adc_z(TMP3); a.cmp_z(PX); a.bcc("land_nx")
    a.lda_z(PY); a.clc(); a.adc_i(16); a.sec(); a.sbc_z(TMP2)
    a.cmp_i(8); a.bcs("land_nx")
    a.lda_z(TMP2); a.sec(); a.sbc_i(16); a.sta_z(PY)
    a.lda_i(0); a.sta_z(VY)
    a.lda_i(1); a.sta_z(GROUND)
    a.rts()
    a.label("land_nx")
    a.inx(); a.cpx_i(4); a.bne("land_lp")
    a.label("land_out")
    a.rts()

    a.label("move_bullet")
    a.lda_z(BON); a.beq("bul_rts")
    a.lda_z(BD); a.beq("bul_left")
    a.lda_z(BX); a.clc(); a.adc_i(3); a.sta_z(BX)
    a.cmp_i(248); a.bcc("bul_rts")
    a.lda_i(0); a.sta_z(BON); a.rts()
    a.label("bul_left")
    a.lda_z(BX); a.cmp_i(11); a.bcc("bul_kill")
    a.sec(); a.sbc_i(3); a.sta_z(BX); a.rts()
    a.label("bul_kill")
    a.lda_i(0); a.sta_z(BON)
    a.label("bul_rts")
    a.rts()

    a.label("idx_times6")
    a.lda_z(IDX); a.sta_z(TMP); a.asl(); a.clc(); a.adc_z(TMP); a.asl(); a.tay()
    a.rts()

    a.label("move_enemies")
    a.lda_i(0); a.sta_z(IDX)
    a.label("en_lp")
    a.jsr("idx_times6")
    a.lda_ay(ENT + 3); a.beq("en_nx")
    a.lda_ay(ENT); a.clc(); a.adc_ay(ENT + 2); a.sta_ay(ENT)
    a.cmp_i(8); a.bcs("en_not_left")
    a.lda_i(1); a.sta_ay(ENT + 2)
    a.label("en_not_left")
    a.lda_ay(ENT); a.cmp_i(216); a.bcc("en_nx")
    a.lda_i(255); a.sta_ay(ENT + 2)
    a.label("en_nx")
    a.inc_z(IDX); a.lda_z(IDX); a.cmp_i(3); a.bcs("en_rts")
    a.jmp("en_lp")
    a.label("en_rts")
    a.rts()

    a.label("check_hits")
    a.jsr("bullet_hits"); a.jsr("player_hits"); a.rts()

    a.label("bullet_hits")
    a.lda_z(BON); a.beq("bh_rts")
    a.lda_i(0); a.sta_z(IDX)
    a.label("bh_lp")
    a.jsr("idx_times6")
    a.lda_ay(ENT + 3); a.beq("bh_nx")
    a.lda_z(BX); a.clc(); a.adc_i(6); a.cmp_ay(ENT); a.bcc("bh_nx")
    a.lda_ay(ENT); a.clc(); a.adc_i(12); a.cmp_z(BX); a.bcc("bh_nx")
    a.lda_z(BY); a.clc(); a.adc_i(6); a.cmp_ay(ENT + 1); a.bcc("bh_nx")
    a.lda_ay(ENT + 1); a.clc(); a.adc_i(12); a.cmp_z(BY); a.bcc("bh_nx")
    a.lda_ay(ENT + 5); a.sec(); a.sbc_i(1); a.sta_ay(ENT + 5)
    a.bne("bh_live")
    a.lda_i(0); a.sta_ay(ENT + 3)
    a.label("bh_live")
    a.lda_i(0); a.sta_z(BON)
    a.jsr("blip"); a.rts()
    a.label("bh_nx")
    a.inc_z(IDX); a.lda_z(IDX); a.cmp_i(3); a.bcs("bh_rts")
    a.jmp("bh_lp")
    a.label("bh_rts")
    a.rts()

    a.label("player_hits")
    a.lda_z(STATE); a.cmp_i(1); a.bne("ph_rts")
    a.lda_z(INV); a.bne("ph_rts")
    a.lda_i(0); a.sta_z(IDX)
    a.label("ph_lp")
    a.jsr("idx_times6")
    a.lda_ay(ENT + 3); a.beq("ph_nx")
    a.lda_z(PX); a.clc(); a.adc_i(14); a.cmp_ay(ENT); a.bcc("ph_nx")
    a.lda_ay(ENT); a.clc(); a.adc_i(12); a.cmp_z(PX); a.bcc("ph_nx")
    a.lda_z(PY); a.clc(); a.adc_i(16); a.cmp_ay(ENT + 1); a.bcc("ph_nx")
    a.lda_ay(ENT + 1); a.clc(); a.adc_i(12); a.cmp_z(PY); a.bcc("ph_nx")
    a.lda_z(RISING); a.bne("ph_hurt")
    a.lda_z(VY); a.beq("ph_hurt")
    a.lda_z(PY); a.clc(); a.adc_i(16); a.sec(); a.sbc_ay(ENT + 1)
    a.cmp_i(8); a.bcs("ph_hurt")
    a.lda_i(0); a.sta_ay(ENT + 3)
    a.lda_i(1); a.sta_z(RISING)
    a.lda_i(4); a.sta_z(VY)
    a.lda_i(0); a.sta_z(GROUND)
    a.jsr("beep"); a.rts()
    a.label("ph_hurt")
    a.dec_z(LIVES)
    a.lda_i(90); a.sta_z(INV)
    a.jsr("blip")
    a.lda_z(LIVES); a.bne("ph_rts")
    a.jsr("go_over")
    a.label("ph_rts")
    a.rts()
    a.label("ph_nx")
    a.inc_z(IDX); a.lda_z(IDX); a.cmp_i(3); a.bcs("ph_rts")
    a.jmp("ph_lp")

    a.label("check_nuts")
    a.lda_z(STATE); a.cmp_i(1); a.bne("nut_rts")
    a.lda_i(0); a.sta_z(IDX)
    a.label("nut_lp")
    a.lda_z(IDX); a.sta_z(TMP); a.asl(); a.clc(); a.adc_z(TMP); a.tay()
    a.lda_ay(NUT + 2); a.beq("nut_nx")
    a.lda_z(PX); a.clc(); a.adc_i(14); a.cmp_ay(NUT); a.bcc("nut_nx")
    a.lda_ay(NUT); a.clc(); a.adc_i(8); a.cmp_z(PX); a.bcc("nut_nx")
    a.lda_z(PY); a.clc(); a.adc_i(16); a.cmp_ay(NUT + 1); a.bcc("nut_nx")
    a.lda_ay(NUT + 1); a.clc(); a.adc_i(8); a.cmp_z(PY); a.bcc("nut_nx")
    a.lda_i(0); a.sta_ay(NUT + 2)
    a.jsr("beep")
    a.label("nut_nx")
    a.inc_z(IDX); a.lda_z(IDX); a.cmp_i(4); a.bcs("nut_rts")
    a.jmp("nut_lp")
    a.label("nut_rts")
    a.rts()

    a.label("hang_control")
    a.lda_z(HANG); a.beq("hang_no")
    a.lda_z(JOY); a.and_i(0x01); a.beq("hang_try_left")
    a.lda_z(SWING); a.cmp_i(20); a.bcs("hang_placed")
    a.inc_z(SWING); a.jmp("hang_placed")
    a.label("hang_try_left")
    a.lda_z(JOY); a.and_i(0x02); a.beq("hang_placed")
    a.lda_z(SWING); a.beq("hang_placed")
    a.dec_z(SWING)
    a.label("hang_placed")
    a.lda_z(HANG); a.sec(); a.sbc_i(1); a.sta_z(IDX)
    a.jsr("idx_times6")
    a.lda_ay(ENT); a.clc(); a.adc_z(SWING); a.sec(); a.sbc_i(16); a.sta_z(PX)
    a.lda_ay(ENT + 1); a.sta_z(PY)
    a.lda_i(0); a.sta_z(GROUND); a.sta_z(RISING); a.sta_z(VY)
    a.lda_z(JOY); a.and_i(0x80); a.bne("hang_keep")
    a.lda_i(0); a.sta_z(HANG)
    a.lda_i(1); a.sta_z(RISING)
    a.lda_i(4); a.sta_z(VY)
    a.label("hang_keep")
    a.sec(); a.rts()
    a.label("hang_no")
    a.clc(); a.rts()

    a.label("try_grab")
    a.lda_z(HANG); a.bne("grab_out")
    a.lda_z(GROUND); a.bne("grab_out")
    a.lda_z(JOY); a.and_i(0x80); a.beq("grab_out")
    a.lda_i(0); a.sta_z(IDX)
    a.label("grab_lp")
    a.jsr("idx_times6")
    a.lda_z(PX); a.clc(); a.adc_i(10); a.cmp_ay(ENT); a.bcc("grab_nx")
    a.lda_ay(ENT); a.clc(); a.adc_i(10); a.cmp_z(PX); a.bcc("grab_nx")
    a.lda_z(PY); a.clc(); a.adc_i(8); a.cmp_ay(ENT + 1); a.bcc("grab_nx")
    a.lda_ay(ENT + 1); a.clc(); a.adc_i(8); a.cmp_z(PY); a.bcc("grab_nx")
    a.lda_z(IDX); a.clc(); a.adc_i(1); a.sta_z(HANG)
    a.lda_i(10); a.sta_z(SWING)
    a.lda_i(0); a.sta_z(GROUND); a.sta_z(RISING); a.sta_z(VY)
    a.jsr("beep"); a.rts()
    a.label("grab_nx")
    a.inc_z(IDX); a.lda_z(IDX); a.cmp_i(3); a.bcs("grab_out")
    a.jmp("grab_lp")
    a.label("grab_out")
    a.rts()

    a.label("whip_tick")
    a.lda_z(WHIP); a.beq("whip_arm")
    a.dec_z(WHIP); a.rts()
    a.label("whip_arm")
    a.jsr("select_edge"); a.bcc("whip_out")
    a.lda_i(18); a.sta_z(WHIP)
    a.jsr("blip")
    a.label("whip_out")
    a.rts()

    a.label("check_flag")
    a.lda_z(STATE); a.cmp_i(1); a.bne("flag_rts")
    a.lda_z(GROUND); a.beq("flag_rts")
    a.lda_z(PX); a.clc(); a.adc_i(8); a.cmp_z(FLAG); a.bcc("flag_rts")
    a.inc_z(LEVEL)
    a.lda_z(LEVEL); a.cmp_i(3); a.bcs("flag_win")
    a.jsr("begin_level"); a.rts()
    a.label("flag_win")
    a.jsr("go_win")
    a.label("flag_rts")
    a.rts()

    a.label("put_spr")
    a.ldx_z(OAMI); a.pha()
    a.lda_z(TMP); a.sec(); a.sbc_i(1); a.sta_ax(0x0200)
    a.inx(); a.lda_z(TMP2); a.sta_ax(0x0200)
    a.inx(); a.lda_z(TMP3); a.sta_ax(0x0200)
    a.inx(); a.pla(); a.sta_ax(0x0200)
    a.inx(); a.stx_z(OAMI); a.rts()

    a.label("oam_hide")
    a.ldx_z(OAMI); a.lda_i(0xF0)
    a.label("hide_lp")
    a.sta_ax(0x0200); a.inx(); a.bne("hide_lp")
    a.rts()

    a.label("oam_mascot")
    a.lda_i(184); a.sta_z(TMP)
    a.lda_i(0); a.sta_z(TMP2); a.sta_z(TMP3)
    a.lda_i(120); a.jsr("put_spr")
    a.lda_i(192); a.sta_z(TMP)
    a.lda_z(FRAME); a.and_i(8); a.beq("mascot_b")
    a.lda_i(2); a.bne("mascot_set")
    a.label("mascot_b")
    a.lda_i(1)
    a.label("mascot_set")
    a.sta_z(TMP2)
    a.lda_i(1); a.sta_z(TMP3)
    a.lda_i(120); a.jsr("put_spr")
    a.rts()

    a.label("oam_player")
    a.lda_z(INV); a.beq("draw_pl")
    a.lda_z(FRAME); a.and_i(4); a.bne("skip_pl")
    a.label("draw_pl")
    a.lda_i(0); a.sta_z(TMP3)
    a.lda_z(FACE); a.bne("face_r")
    a.lda_i(0x40); a.sta_z(TMP3)
    a.label("face_r")
    a.lda_z(PY); a.sta_z(TMP)
    a.lda_i(0); a.sta_z(TMP2)
    a.lda_z(PX); a.jsr("put_spr")
    a.lda_z(PY); a.clc(); a.adc_i(8); a.sta_z(TMP)
    a.lda_z(ANIM); a.and_i(8); a.beq("body_a")
    a.lda_i(2); a.bne("body_set")
    a.label("body_a")
    a.lda_i(1)
    a.label("body_set")
    a.sta_z(TMP2)
    a.lda_z(FACE); a.bne("body_face_r")
    a.lda_i(0x41); a.jmp("body_attr")
    a.label("body_face_r")
    a.lda_i(0x01)
    a.label("body_attr")
    a.sta_z(TMP3)
    a.lda_z(PX); a.jsr("put_spr")
    a.label("skip_pl")
    a.rts()

    a.label("oam_enemies")
    a.lda_i(0); a.sta_z(IDX)
    a.label("oed_lp")
    a.jsr("idx_times6")
    a.lda_ay(ENT + 3); a.beq("oed_nx")
    a.lda_ay(ENT + 1); a.sta_z(TMP)
    a.lda_i(4); a.sta_z(TMP2)
    a.lda_i(1); a.sta_z(TMP3)
    a.lda_ay(ENT); a.jsr("put_spr")
    a.lda_ay(ENT + 4); a.cmp_i(2); a.bne("oed_nx")
    a.lda_ay(ENT + 1); a.sta_z(TMP)
    a.lda_i(4); a.sta_z(TMP2)
    a.lda_i(1); a.sta_z(TMP3)
    a.lda_ay(ENT); a.clc(); a.adc_i(8); a.jsr("put_spr")
    a.label("oed_nx")
    a.inc_z(IDX); a.lda_z(IDX); a.cmp_i(3); a.bcs("oed_rts")
    a.jmp("oed_lp")
    a.label("oed_rts")
    a.rts()

    a.label("oam_nuts")
    a.lda_i(0); a.sta_z(IDX)
    a.label("ond_lp")
    a.lda_z(IDX); a.sta_z(TMP); a.asl(); a.clc(); a.adc_z(TMP); a.tay()
    a.lda_ay(NUT + 2); a.beq("ond_nx")
    a.lda_ay(NUT + 1); a.sta_z(TMP)
    a.lda_i(5); a.sta_z(TMP2)
    a.lda_i(2); a.sta_z(TMP3)
    a.lda_ay(NUT); a.jsr("put_spr")
    a.label("ond_nx")
    a.inc_z(IDX); a.lda_z(IDX); a.cmp_i(4); a.bcs("ond_rts")
    a.jmp("ond_lp")
    a.label("ond_rts")
    a.rts()

    a.label("oam_bullet")
    a.lda_z(BON); a.beq("ob_rts")
    a.lda_z(BY); a.sta_z(TMP)
    a.lda_i(5); a.sta_z(TMP2)
    a.lda_i(2); a.sta_z(TMP3)
    a.lda_z(BX); a.jsr("put_spr")
    a.label("ob_rts")
    a.rts()

    a.label("oam_tags")
    a.lda_i(0); a.sta_z(IDX)
    a.label("ot_lp")
    a.jsr("idx_times6")
    a.lda_ay(ENT); a.beq("ot_nx")
    a.lda_ay(ENT + 1); a.sta_z(TMP)
    a.lda_i(8); a.sta_z(TMP2)
    a.lda_i(3); a.sta_z(TMP3)
    a.lda_ay(ENT); a.jsr("put_spr")
    a.label("ot_nx")
    a.inc_z(IDX); a.lda_z(IDX); a.cmp_i(3); a.bcs("ot_rts")
    a.jmp("ot_lp")
    a.label("ot_rts")
    a.rts()

    a.label("oam_whip")
    a.lda_z(WHIP); a.beq("ow_rts")
    a.lda_z(FACE); a.beq("ow_left")
    a.lda_z(PY); a.clc(); a.adc_i(4); a.sta_z(TMP)
    a.lda_i(9); a.sta_z(TMP2)
    a.lda_i(2); a.sta_z(TMP3)
    a.lda_z(PX); a.clc(); a.adc_i(8); a.jsr("put_spr")
    a.lda_z(PY); a.clc(); a.adc_i(4); a.sta_z(TMP)
    a.lda_i(10); a.sta_z(TMP2)
    a.lda_i(2); a.sta_z(TMP3)
    a.lda_z(PX); a.clc(); a.adc_i(16); a.jsr("put_spr")
    a.rts()
    a.label("ow_left")
    a.lda_z(PY); a.clc(); a.adc_i(4); a.sta_z(TMP)
    a.lda_i(9); a.sta_z(TMP2)
    a.lda_i(0x42); a.sta_z(TMP3)
    a.lda_z(PX); a.sec(); a.sbc_i(8); a.jsr("put_spr")
    a.lda_z(PY); a.clc(); a.adc_i(4); a.sta_z(TMP)
    a.lda_i(10); a.sta_z(TMP2)
    a.lda_i(0x42); a.sta_z(TMP3)
    a.lda_z(PX); a.sec(); a.sbc_i(16); a.jsr("put_spr")
    a.label("ow_rts")
    a.rts()

    a.label("oam_hearts")
    a.lda_i(0); a.sta_z(IDX)
    a.label("oh_lp")
    a.lda_z(IDX); a.cmp_z(LIVES); a.bcs("oh_rts")
    a.lda_z(IDX); a.asl(); a.asl(); a.asl()
    a.clc(); a.adc_z(IDX); a.clc(); a.adc_z(IDX); a.clc(); a.adc_i(12)
    a.pha()
    a.lda_i(12); a.sta_z(TMP)
    a.lda_i(7); a.sta_z(TMP2)
    a.lda_i(3); a.sta_z(TMP3)
    a.pla(); a.jsr("put_spr")
    a.inc_z(IDX); a.jmp("oh_lp")
    a.label("oh_rts")
    a.rts()

    a.label("build_oam")
    a.lda_i(0); a.sta_z(OAMI)
    a.lda_z(STATE); a.cmp_i(1); a.beq("oam_play")
    a.jsr("oam_mascot"); a.jmp("oam_hide")
    a.label("oam_play")
    a.jsr("oam_player"); a.jsr("oam_tags")
    a.jsr("oam_bullet"); a.jsr("oam_whip"); a.jmp("oam_hide")

    a.label("main")
    a.jsr("wait_nmi")
    a.inc_z(FRAME)
    a.jsr("read_joy")
    a.lda_z(STATE); a.beq("idle")
    a.cmp_i(1); a.beq("playing")
    a.jmp("idle")
    a.label("playing")
    a.jsr("move_player"); a.jsr("move_bullet")
    a.jsr("build_oam"); a.jmp("frame_end")
    a.label("idle")
    a.jsr("start_edge"); a.bcc("idle_draw")
    a.jsr("new_game"); a.jmp("frame_end")
    a.label("idle_draw")
    a.jsr("build_oam")
    a.label("frame_end")
    a.lda_z(JOY); a.sta_z(PREV)
    a.jmp("main")

    a.label("reset")
    a.sei(); a.cld()
    a.ldx_i(0x40); a.stx_a(0x4017)
    a.ldx_i(0xFF); a.txs(); a.inx()
    a.stx_a(0x2000); a.stx_a(0x2001); a.stx_a(0x4010)
    a.label("vb1")
    a.bit_a(0x2002); a.bpl("vb1")
    a.txa()
    a.label("clr")
    a.sta_ax(0x0000); a.sta_ax(0x0100); a.sta_ax(0x0200); a.sta_ax(0x0300)
    a.sta_ax(0x0400); a.sta_ax(0x0500); a.sta_ax(0x0600); a.sta_ax(0x0700)
    a.inx(); a.bne("clr")
    a.label("vb2")
    a.bit_a(0x2002); a.bpl("vb2")
    a.lda_i(0); a.sta_a(0x4015)
    a.lda_i(0x0F); a.sta_a(0x4015)
    a.jsr("go_title")
    a.jmp("main")

    code_end = len(a.buf)

    def table(name, labels):
        a.label(name + "_lo")
        for lab in labels:
            a.lo(lab)
        a.label(name + "_hi")
        for lab in labels:
            a.hi(lab)

    table("nt", ["nt0", "nt1", "nt2"])
    table("pal", ["pal0", "pal1", "pal2"])
    table("ent", ["ent0", "ent1", "ent2"])
    a.label("title_nt"); a.db(TITLE_NT)
    a.label("win_nt"); a.db(WIN_NT)
    a.label("over_nt"); a.db(OVER_NT)
    for i, blob in enumerate(NTS):
        a.label("nt%d" % i); a.db(blob)
    for i, blob in enumerate(PALS):
        a.label("pal%d" % i); a.db(blob)
    for i, blob in enumerate(ENTS):
        a.label("ent%d" % i); a.db(blob)
    a.pad_vectors()
    a.resolve()
    if len(a.buf) != 16384:
        raise SystemExit("PRG %d" % len(a.buf))
    print("code %d octets, PRG 16384" % code_end)
    return a


class Machine:
    def __init__(self, prg, main_addr):
        self.prg = prg
        self.ram = bytearray(2048)
        self.vram = bytearray(0x4000)
        self.a = self.x = self.y = 0
        self.sp = 0xFD
        self.n = self.v = self.z = self.c = False
        self.i = True
        self.pc = self.r16(0xFFFC)
        self.ppu_ctrl = 0
        self.ppu_addr = 0
        self.ppu_hi = True
        self.buttons = 0
        self.shift = 0
        self.in_nmi = False
        self.steps = 0
        self.since_nmi = 0
        self.trace = []
        self.main_addr = main_addr
        self.visit = 0
        self.hook = None

    def r8(self, a):
        a &= 0xFFFF
        if a < 0x2000:
            return self.ram[a & 0x7FF]
        if a == 0x2002:
            return 0x80
        if a == 0x4016:
            bit = (self.shift >> 7) & 1
            self.shift = (self.shift << 1) & 255
            return bit
        if a >= 0xC000:
            return self.prg[a - 0xC000]
        return 0

    def r16(self, a):
        return self.r8(a) | (self.r8((a + 1) & 0xFFFF) << 8)

    def w8(self, a, v):
        a &= 0xFFFF
        v &= 255
        if a < 0x2000:
            self.ram[a & 0x7FF] = v
        elif a == 0x2000:
            self.ppu_ctrl = v
        elif a == 0x2005:
            self.ppu_hi = not self.ppu_hi
        elif a == 0x2006:
            if self.ppu_hi:
                self.ppu_addr = (v & 0x3F) << 8
                self.ppu_hi = False
            else:
                self.ppu_addr = (self.ppu_addr & 0xFF00) | v
                self.ppu_hi = True
        elif a == 0x2007:
            self.vram[self.ppu_addr & 0x3FFF] = v
            self.ppu_addr = (self.ppu_addr + 1) & 0x3FFF
        elif a == 0x4016 and (v & 1):
            self.shift = self.buttons

    def set_zn(self, v):
        v &= 255
        self.z = v == 0
        self.n = bool(v & 128)
        return v

    def push(self, v):
        self.w8(0x100 + self.sp, v)
        self.sp = (self.sp - 1) & 255

    def pop(self):
        self.sp = (self.sp + 1) & 255
        return self.r8(0x100 + self.sp)

    def fetch(self):
        v = self.r8(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return v

    def fetch16(self):
        lo = self.fetch()
        hi = self.fetch()
        return lo | (hi << 8)

    def zp(self):
        return self.ram[self.fetch()]

    def step(self):
        if self.pc == self.main_addr and not self.in_nmi:
            self.visit += 1
            if self.hook:
                self.hook(self)
        op_pc = self.pc
        op = self.fetch()
        self.trace.append((op_pc, op))
        if len(self.trace) > 40:
            self.trace.pop(0)
        self.exec(op)
        self.steps += 1
        self.since_nmi += 1
        if self.ppu_ctrl & 0x80 and not self.in_nmi and self.since_nmi >= 280:
            self.since_nmi = 0
            self.push((self.pc >> 8) & 255)
            self.push(self.pc & 255)
            self.push((self.n << 7) | (self.v << 6) | 0x20 | (self.i << 2) | (self.z << 1) | self.c)
            self.i = True
            self.pc = self.r16(0xFFFA)
            self.in_nmi = True

    def branch(self, cond):
        off = self.fetch()
        if off & 128:
            off -= 256
        if cond:
            self.pc = (self.pc + off) & 0xFFFF

    def cmp(self, reg, v):
        self.c = reg >= v
        self.set_zn(reg - v)

    def exec(self, op):
        if op == 0xA9:
            self.a = self.set_zn(self.fetch())
        elif op == 0xA2:
            self.x = self.set_zn(self.fetch())
        elif op == 0xA0:
            self.y = self.set_zn(self.fetch())
        elif op == 0xA5:
            self.a = self.set_zn(self.zp())
        elif op == 0xA6:
            self.x = self.set_zn(self.zp())
        elif op == 0x85:
            self.w8(self.fetch(), self.a)
        elif op == 0x86:
            self.w8(self.fetch(), self.x)
        elif op == 0xAD:
            self.a = self.set_zn(self.r8(self.fetch16()))
        elif op == 0x8D:
            self.w8(self.fetch16(), self.a)
        elif op == 0x8E:
            self.w8(self.fetch16(), self.x)
        elif op == 0x9D:
            self.w8((self.fetch16() + self.x) & 0xFFFF, self.a)
        elif op == 0xB9:
            self.a = self.set_zn(self.r8((self.fetch16() + self.y) & 0xFFFF))
        elif op == 0x99:
            self.w8((self.fetch16() + self.y) & 0xFFFF, self.a)
        elif op == 0x79:
            self.adc(self.r8((self.fetch16() + self.y) & 0xFFFF))
        elif op == 0xD9:
            self.cmp(self.a, self.r8((self.fetch16() + self.y) & 0xFFFF))
        elif op == 0xF9:
            self.sbc(self.r8((self.fetch16() + self.y) & 0xFFFF))
        elif op == 0xBD:
            self.a = self.set_zn(self.r8((self.fetch16() + self.x) & 0xFFFF))
        elif op == 0xB1:
            z = self.fetch()
            base = self.r8(z) | (self.r8((z + 1) & 255) << 8)
            self.a = self.set_zn(self.r8((base + self.y) & 0xFFFF))
        elif op == 0xC9:
            self.cmp(self.a, self.fetch())
        elif op == 0xC5:
            self.cmp(self.a, self.zp())
        elif op == 0xE0:
            self.cmp(self.x, self.fetch())
        elif op == 0xC0:
            self.cmp(self.y, self.fetch())
        elif op == 0x29:
            self.a = self.set_zn(self.a & self.fetch())
        elif op == 0x69:
            self.adc(self.fetch())
        elif op == 0x65:
            self.adc(self.zp())
        elif op == 0xE9:
            self.sbc(self.fetch())
        elif op == 0xE5:
            self.sbc(self.zp())
        elif op == 0xE6:
            z = self.fetch(); self.w8(z, self.set_zn(self.r8(z) + 1))
        elif op == 0xC6:
            z = self.fetch(); self.w8(z, self.set_zn(self.r8(z) - 1))
        elif op == 0x2C:
            v = self.r8(self.fetch16())
            self.n = bool(v & 128); self.v = bool(v & 64); self.z = (self.a & v) == 0
        elif op == 0x4C:
            self.pc = self.fetch16()
        elif op == 0x20:
            target = self.fetch16()
            ret = (self.pc - 1) & 0xFFFF
            self.push(ret >> 8); self.push(ret & 255)
            self.pc = target
        elif op == 0x60:
            lo = self.pop(); hi = self.pop()
            self.pc = ((hi << 8) | lo) + 1 & 0xFFFF
        elif op == 0x40:
            p = self.pop()
            self.c = bool(p & 1); self.z = bool(p & 2); self.i = bool(p & 4)
            self.v = bool(p & 64); self.n = bool(p & 128)
            lo = self.pop(); hi = self.pop()
            self.pc = lo | (hi << 8)
            self.in_nmi = False
        elif op == 0xD0:
            self.branch(not self.z)
        elif op == 0xF0:
            self.branch(self.z)
        elif op == 0x90:
            self.branch(not self.c)
        elif op == 0xB0:
            self.branch(self.c)
        elif op == 0x10:
            self.branch(not self.n)
        elif op == 0x0A:
            self.c = bool(self.a & 128); self.a = self.set_zn(self.a << 1)
        elif op == 0x4A:
            self.c = bool(self.a & 1); self.a = self.set_zn(self.a >> 1)
        elif op == 0x26:
            z = self.fetch(); v = self.r8(z)
            nc = bool(v & 128)
            self.w8(z, self.set_zn(((v << 1) | (1 if self.c else 0)) & 255))
            self.c = nc
        elif op == 0x18:
            self.c = False
        elif op == 0x38:
            self.c = True
        elif op == 0x78:
            self.i = True
        elif op == 0xD8:
            pass
        elif op == 0x48:
            self.push(self.a)
        elif op == 0x68:
            self.a = self.set_zn(self.pop())
        elif op == 0xAA:
            self.x = self.set_zn(self.a)
        elif op == 0xA8:
            self.y = self.set_zn(self.a)
        elif op == 0x8A:
            self.a = self.set_zn(self.x)
        elif op == 0x98:
            self.a = self.set_zn(self.y)
        elif op == 0x9A:
            self.sp = self.x
        elif op == 0xE8:
            self.x = self.set_zn(self.x + 1)
        elif op == 0xCA:
            self.x = self.set_zn(self.x - 1)
        elif op == 0xC8:
            self.y = self.set_zn(self.y + 1)
        else:
            raise RuntimeError("opcode %02X a $%04X" % (op, self.trace[-1][0]))

    def adc(self, v):
        r = self.a + v + (1 if self.c else 0)
        self.c = r > 255
        self.a = self.set_zn(r)

    def sbc(self, v):
        self.adc(v ^ 255)

    def run(self, limit):
        while self.steps < limit:
            self.step()
        return self


def snap(m):
    return dict(pc=m.pc, state=m.ram[STATE], level=m.ram[LEVEL], lives=m.ram[LIVES],
                px=m.ram[PX], py=m.ram[PY], vx=m.ram[VX], vy=m.ram[VY], rising=m.ram[RISING],
                ground=m.ram[GROUND], bon=m.ram[BON], bx=m.ram[BX], bd=m.ram[BD],
                hang=m.ram[HANG], whip=m.ram[WHIP], swing=m.ram[SWING],
                visit=m.visit, steps=m.steps)


def fail(m, msg):
    print("ECHEC", msg)
    print(snap(m))
    print("trace:")
    for pc, op in m.trace:
        print("  $%04X %02X" % (pc, op))
    raise SystemExit(1)


def run_case(prg, main_addr, hook, limit=800000):
    m = Machine(prg, main_addr)
    m.hook = hook
    try:
        while m.steps < limit and m.visit < 40:
            m.step()
    except RuntimeError as exc:
        fail(m, str(exc))
    return m


def smoke(prg, labels):
    main = labels["main"]
    checks = {}

    def play(m):
        v = m.visit
        if v in checks:
            checks[v](m)
        if v == 3:
            m.buttons = 0x10
        elif 4 <= v <= 23:
            m.buttons = 0x01
        elif v in (24, 25):
            m.buttons = 0x80
        elif v == 31:
            m.buttons = 0x40
        else:
            m.buttons = 0

    def expect(visit, fn):
        checks[visit] = fn

    expect(2, lambda m: need(m, m.vram[0x2000:0x2400] == TITLE_NT, "ecran titre") or need(
        m, m.vram[0x3F00:0x3F20] == PALS[0], "palette titre"))
    expect(4, lambda m: need(m, m.ram[STATE] == 1 and m.ram[PX] == 24 and m.ram[PY] == 184
                              and m.ram[LIVES] == 3 and m.ram[LEVEL] == 0
                              and bytes(m.ram[ENT:ENT + 43]) == ENTS[0]
                              and m.vram[0x2000:0x2400] == NTS[0], "depart parc"))
    expect(24, lambda m: need(m, m.ram[PX] == 63 and m.ram[PY] == 184 and m.ram[GROUND] == 1
                              and m.ram[VX] == 2, "marche droite"))
    expect(25, lambda m: need(m, m.ram[RISING] == 1 and m.ram[VY] == 9 and m.ram[PY] == 184,
                               "saut"))
    expect(26, lambda m: need(m, m.ram[PY] == 175 and m.ram[VY] == 8, "montee"))
    expect(32, lambda m: need(m, m.ram[BON] == 1 and m.ram[BX] == 81 and m.ram[BD] == 1,
                               "tir"))
    m = run_case(prg, main, play)
    if m.visit < 32:
        fail(m, "boucle principale non atteinte (%d)" % m.visit)
    print("jeu: titre, marche, saut, tir OK en %d pas" % m.steps)

    def course(m):
        if m.visit == 3:
            m.buttons = 0x10
        elif 4 <= m.visit <= 10:
            m.buttons = 0x41
        else:
            m.buttons = 0
        if m.visit == 8:
            need(m, m.ram[PX] == 34 and m.ram[VX] == 4 and m.ram[FACE] == 1, "course")
            m.visit = 40

    run_case(prg, main, course)
    print("course: B tenu accelere jusqu'a 4 px OK")

    def short_hop(m):
        if m.visit == 3:
            m.buttons = 0x10
        elif m.visit == 8:
            m.buttons = 0x80
        else:
            m.buttons = 0
        if m.visit == 10:
            need(m, m.ram[PY] == 179 and m.ram[VY] == 4 and m.ram[RISING] == 1, "petit saut")
            m.visit = 40

    run_case(prg, main, short_hop)
    print("petit saut: A tapote coupe la montee OK")

    def death(m):
        if m.visit == 3:
            m.buttons = 0x10
        else:
            m.buttons = 0
        if m.visit == 5:
            m.ram[LIVES] = 1
            m.ram[INV] = 0
            m.ram[PX] = 168
            m.ram[PY] = 184
            m.ram[VY] = 0
            m.ram[RISING] = 0
            m.ram[ENT:ENT + 6] = bytes((168, 192, 1, 1, 0, 1))
        if m.visit == 6:
            need(m, m.ram[STATE] == 1 and m.ram[LIVES] == 1, "raisins inertes")
            m.visit = 40

    run_case(prg, main, death)
    print("contact: les raisins ne font rien OK")

    def hang(m):
        if m.visit == 3:
            m.buttons = 0x10
        elif m.visit == 5:
            m.ram[PX] = 48
            m.ram[PY] = 184
            m.ram[VX] = 0
            m.ram[VY] = 0
            m.ram[RISING] = 0
            m.ram[GROUND] = 1
            m.ram[HANG] = 0
            m.buttons = 0x80
        elif m.visit == 6:
            m.buttons = 0x80
        elif m.visit == 7:
            need(m, m.ram[HANG] == 1 and m.ram[PY] == 176 and m.ram[GROUND] == 0, "etiquette")
            m.buttons = 0
        elif m.visit == 8:
            need(m, m.ram[HANG] == 0 and m.ram[RISING] == 1 and m.ram[VY] == 4, "lacher")
            m.visit = 40
        else:
            m.buttons = 0

    run_case(prg, main, hang)
    print("etiquette: A sous le carton accroche, lacher A decroche OK")

    def whip(m):
        if m.visit == 3:
            m.buttons = 0x10
        elif m.visit == 5:
            m.buttons = 0x20
        elif m.visit == 6:
            need(m, m.ram[WHIP] == 18, "fouet")
            m.visit = 40
        else:
            m.buttons = 0

    run_case(prg, main, whip)
    print("fouet: Select arme le coup OK")

    def land(m):
        if m.visit == 3:
            m.buttons = 0x10
        elif m.visit == 5:
            m.ram[PX] = 40
            m.ram[PY] = 130
            m.ram[VX] = 0
            m.ram[VY] = 0
            m.ram[RISING] = 0
            m.ram[GROUND] = 0
            m.ram[HANG] = 0
            m.buttons = 0
        elif m.visit == 20:
            need(m, m.ram[GROUND] == 1 and m.ram[PY] == 144 and m.ram[HANG] == 0, "comptoir gauche")
            m.visit = 40
        else:
            m.buttons = 0

    run_case(prg, main, land)
    print("chute: atterrit sur le comptoir gauche OK")

    def mid(m):
        if m.visit == 3:
            m.buttons = 0x10
        elif m.visit == 5:
            m.ram[PX] = 78
            m.ram[PY] = 144
            m.ram[VX] = 0
            m.ram[VY] = 0
            m.ram[RISING] = 0
            m.ram[GROUND] = 1
            m.ram[FACE] = 1
            m.ram[HANG] = 0
            m.buttons = 0x81
        elif m.visit > 5:
            m.buttons = 0x81
            if m.ram[GROUND] == 1 and m.ram[PY] == 112:
                m.visit = 40
            elif m.visit > 36:
                fail(m, "comptoir du milieu")
        else:
            m.buttons = 0

    run_case(prg, main, mid)
    print("saut tenu: du comptoir gauche au milieu OK")


def need(m, cond, msg):
    if not cond:
        fail(m, msg)
    return True


def render(chr_rom, nt, pal, sprites, path):
    w, h = 256, 240
    rgb = bytearray(w * h * 3)
    bg = chr_rom[:4096]
    sp = chr_rom[4096:]
    for ty in range(30):
        for tx in range(32):
            tile_i = nt[ty * 32 + tx]
            tile = bg[tile_i * 16:(tile_i + 1) * 16]
            for row in range(8):
                lo = tile[row]
                hi = tile[row + 8]
                for col in range(8):
                    bit = 7 - col
                    ci = ((lo >> bit) & 1) | (((hi >> bit) & 1) << 1)
                    attr = nt[0x3C0 + (ty // 4) * 8 + (tx // 4)]
                    quad = ((ty // 2) & 1) * 2 + ((tx // 2) & 1)
                    pal_i = (attr >> (quad * 2)) & 3
                    color = pal[pal_i * 4 + ci]
                    put(rgb, w, tx * 8 + col, ty * 8 + row, NES_PAL[color & 63])
    for sx, sy, tile_i, attr, pal_i in sprites:
        tile = sp[tile_i * 16:(tile_i + 1) * 16]
        base = 16 + pal_i * 4
        for row in range(8):
            lo = tile[row]
            hi = tile[row + 8]
            for col in range(8):
                src = col if attr & 0x40 else 7 - col
                ci = ((lo >> src) & 1) | (((hi >> src) & 1) << 1)
                if ci == 0:
                    continue
                put(rgb, w, sx + col, sy + row, NES_PAL[pal[base + ci] & 63])
    scale = 3
    W, H = w * scale, h * scale
    big = bytearray(W * H * 3)
    for y in range(H):
        sy = y // scale
        for x in range(W):
            sx = x // scale
            i = (sy * w + sx) * 3
            j = (y * W + x) * 3
            big[j:j + 3] = rgb[i:i + 3]
    ppm = path[:-4] + ".ppm"
    with open(ppm, "wb") as f:
        f.write(("P6\n%d %d\n255\n" % (W, H)).encode())
        f.write(big)
    subprocess.check_call(["sips", "-s", "format", "png", ppm, "--out", path],
                          stdout=subprocess.DEVNULL)
    os.remove(ppm)


def put(buf, w, x, y, rgb):
    if 0 <= x < w and 0 <= y < 240:
        i = (y * w + x) * 3
        buf[i:i + 3] = bytes(rgb)


def level_sprites(ent, boss=False):
    sprites = [(24, 184, 0, 0, 0), (24, 192, 1, 0, 0)]
    for i in range(3):
        o = i * 6
        if ent[o + 3] == 0:
            continue
        sprites.append((ent[o], ent[o + 1], 4, 0, 1))
        if ent[o + 4] == 2:
            sprites.append((ent[o] + 8, ent[o + 1], 4, 0, 1))
    for i in range(4):
        o = 18 + i * 3
        if ent[o + 2]:
            sprites.append((ent[o], ent[o + 1], 5, 0, 2))
    for i in range(3):
        sprites.append((12 + i * 10, 12, 7, 0, 3))
    return sprites


def previews(chr_rom):
    tags = [(x, y, 8, 0, 3) for x, y in RAYON_TAGS]
    rayon = [(24, 184, 0, 0, 0), (24, 192, 1, 0, 1)] + tags
    jobs = [
        ("preview-titre.png", TITLE_NT, PALS[0], [(120, 184, 0, 0, 0), (120, 192, 1, 0, 1)]),
        ("preview-rayon.png", NTS[0], PALS[0], rayon),
    ]
    for name, nt, pal, sprites in jobs:
        render(chr_rom, nt, pal, sprites, os.path.join(OUT, name))
    print("aperçus png ecrits")


def install():
    if not os.path.isdir(os.path.join(STICK, "001")):
        print("cle absente, ROM laissee sur le Bureau")
        return
    raw = open(FAV, "rb").read()
    if not raw.endswith(b"\x00") or raw.count(b"\x00") != 1:
        raise SystemExit("favorites.lst inattendu")
    line = (
        "001/%s.zip;%s;%s;%s;%s\n" % (ROM_NAME, ROM_NAME, ROM_NAME.upper(), ROM_NAME, ROM_NAME.upper())
    ).encode()
    body = raw[:-1]
    if line not in body:
        if not body.endswith(b"\n"):
            body += b"\n"
        shutil.copy2(FAV, os.path.join(OUT, "favorites.lst.bak"))
        with open(FAV, "wb") as f:
            f.write(body + line + b"\x00")
    shutil.copyfile(ZIP_PATH, STICK_ZIP)
    back = open(FAV, "rb").read()
    with zipfile.ZipFile(STICK_ZIP) as zf:
        names = zf.namelist()
    if back.count(b"\x00") != 1 or line not in back or names != [ROM_NAME + ".nes"]:
        raise SystemExit("verification cle ratee %s" % names)
    if b"000/dino.zip;" not in back:
        raise SystemExit("anciens favoris perdus")
    print("installe sur la cle:", STICK_ZIP)


def main():
    assert bytes([32 + ord(c) - 65 for c in "RAYON"]) in TITLE_NT
    assert bytes([32 + ord(c) - 65 for c in "RAYON"]) in NTS[0]
    chr_rom = build_chr()
    if len(chr_rom) != 8192:
        raise SystemExit("CHR")
    asm = program()
    prg = bytes(asm.buf)
    rom = bytearray(b"NES\x1a")
    rom += bytes([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    rom += prg + chr_rom
    if len(rom) != 24592 or rom[:4] != b"NES\x1a":
        raise SystemExit("entete")
    with open(NES_PATH, "wb") as f:
        f.write(rom)
    smoke(prg, asm.labels)
    previews(chr_rom)
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(NES_PATH, arcname=ROM_NAME + ".nes")
    with zipfile.ZipFile(ZIP_PATH) as zf:
        info = zf.getinfo(ROM_NAME + ".nes")
        if info.file_size != 24592 or info.compress_type != zipfile.ZIP_DEFLATED:
            raise SystemExit("zip")
    print("ROM", NES_PATH, len(rom))
    install()


if __name__ == "__main__":
    main()
