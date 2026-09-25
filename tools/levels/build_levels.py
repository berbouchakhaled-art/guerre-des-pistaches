"""Build the 3 worlds (Super Mario World style: wide AND tall, upper/lower routes,
secret sky area, hidden ?-blocks, checkpoint, goal) -> js/levels.js

Legend (one char per 40px tile):
  .  air            1  ground / solid deck      2  brick         3  ?-block
  4  ONE-WAY platform (jump through from below, stand on top)
  5 6 / 7 8  pipe top / body     B trampoline    I ice (solid, slippery)
  X  lava (deadly)               H  HIDDEN ?-block (invisible until hit from below)
  C  pistachio       P  power-up       E  peanut enemy   F  flyer   R  raisin (ship)
  S  player start    K  checkpoint flag (ground cell)    G  goal (ground cell)
Rules enforced by tools/levels/check_levels.py: >= 3 free tiles above every standable
tile (never crouch), no low ceilings, start -> checkpoint -> goal reachable with the
hardest (Défi) physics, secret area reachable once the hidden blocks are revealed.
python3 tools/levels/build_levels.py
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
H = 40          # rows (old: 17)
GR = 35         # default ground top row


class Lvl:
    def __init__(self, w, h=H):
        self.w, self.h = w, h
        self.g = [['.'] * w for _ in range(h)]

    def set(self, c, r, ch):
        if 0 <= c < self.w and 0 <= r < self.h:
            self.g[r][c] = ch

    def get(self, c, r):
        return self.g[r][c] if 0 <= c < self.w and 0 <= r < self.h else '.'

    def ground(self, c0, c1, top=GR, ch='1'):
        for c in range(c0, c1 + 1):
            for r in range(top, self.h):
                self.set(c, r, ch)

    def lava(self, c0, c1, top=H - 2):
        for c in range(c0, c1 + 1):
            for r in range(top, self.h):
                self.set(c, r, 'X')

    def plat(self, c0, c1, r, ch='4'):
        for c in range(c0, c1 + 1):
            self.set(c, r, ch)

    def row(self, c0, r, s):
        for i, ch in enumerate(s):
            if ch != ' ':
                self.set(c0 + i, r, ch)

    def pipe(self, c, h, base=GR):
        top = base - h
        self.set(c, top, '5'); self.set(c + 1, top, '6')
        for r in range(top + 1, base):
            self.set(c, r, '7'); self.set(c + 1, r, '8')

    def stairs(self, c0, n, base=GR, up=True, width=1, ch='1'):
        """Mario staircase: n steps of +1 tile (solid down to the bottom)."""
        for i in range(n):
            hgt = i + 1 if up else n - i
            for k in range(width):
                self.ground(c0 + i * width + k, c0 + i * width + k, base - hgt, ch)

    def coins(self, c0, c1, r, step=1):
        for c in range(c0, c1 + 1, step):
            if self.get(c, r) == '.':
                self.set(c, r, 'C')

    def arc(self, c0, c1, r, hgt=2):
        n = c1 - c0
        for i, c in enumerate(range(c0, c1 + 1)):
            t = i / max(1, n)
            rr = r - round(hgt * 4 * t * (1 - t))
            if self.get(c, rr) == '.':
                self.set(c, rr, 'C')

    def rows(self):
        return [''.join(r) for r in self.g]


# ----------------------------------------------------------------------------------
# MONDE 1 · PARC PISTACHE  (170 x 40, old 88 x 17)
# ----------------------------------------------------------------------------------
def park():
    L = Lvl(170)
    # A · départ tranquille (0-22)
    L.ground(0, 22)
    L.set(3, GR - 1, 'S')
    L.row(9, GR - 4, '232')
    L.set(13, GR - 4, '3')
    L.arc(4, 8, GR - 2, 2)
    L.set(16, GR - 4, 'H')                       # bloc caché n°1
    L.set(19, GR - 1, 'E')
    # B · tuyaux + petit trou (23-44)
    L.ground(23, 29)
    L.pipe(24, 2)
    L.set(28, GR - 1, 'E')
    L.ground(33, 46)                             # trou 30-32
    L.arc(29, 33, GR - 3, 2)
    L.pipe(37, 3)
    L.set(35, GR - 1, 'E')
    L.set(43, GR - 1, 'E')
    # entrée de la ROUTE HAUTE : marches de plateformes (traversables)
    L.plat(40, 44, GR - 4)
    L.coins(41, 43, GR - 5)
    L.plat(46, 50, GR - 8)
    L.coins(47, 49, GR - 9)
    L.plat(52, 57, GR - 12)                      # route haute : rangée 23
    # ROUTE BASSE (47-96) : trous, tuyaux, ennemis, ?-blocs
    L.ground(47, 58)
    L.row(51, GR - 4, '323')
    L.set(50, GR - 1, 'E'); L.set(56, GR - 1, 'E')
    L.ground(62, 74)                             # trou 59-61
    L.arc(58, 62, GR - 3, 2)
    L.pipe(66, 2)
    L.set(64, GR - 1, 'E'); L.set(71, GR - 1, 'E')
    L.row(69, GR - 4, '2P2')
    L.ground(79, 110)                            # trou 75-78
    L.arc(74, 79, GR - 4, 3)
    L.set(81, GR - 4, 'H')                       # bloc caché n°2
    L.pipe(86, 4)
    L.set(83, GR - 1, 'E'); L.set(91, GR - 1, 'E')
    L.plat(89, 93, GR - 4)
    L.coins(89, 93, GR - 5)
    # ROUTE HAUTE (52-100) : plateformes, ?-blocs, pièces, quelques ennemis
    L.coins(53, 56, GR - 13)
    L.plat(60, 65, GR - 12); L.set(63, GR - 13, 'E')
    L.row(61, GR - 16, '3 3')
    L.plat(68, 73, GR - 14)
    L.arc(66, 69, GR - 15, 2)
    L.plat(76, 81, GR - 12)
    L.set(78, GR - 16, 'H')                      # bloc caché = marche vers le SECRET
    L.coins(76, 81, GR - 13)
    L.plat(84, 89, GR - 14); L.set(86, GR - 15, 'E')
    L.plat(92, 96, GR - 12)
    L.coins(92, 96, GR - 13)
    L.plat(98, 101, GR - 8)                      # redescente
    L.plat(102, 104, GR - 4)
    # SECRET : jardin dans le ciel (rangées 19 -> 7), plein de pistaches
    L.plat(80, 91, GR - 20)
    L.coins(80, 91, GR - 21)
    L.plat(86, 95, GR - 24)
    L.coins(86, 95, GR - 25)
    L.plat(92, 100, GR - 28)
    L.coins(92, 99, GR - 29)
    L.set(100, GR - 29, 'P')
    # CHECKPOINT (rejonction des routes)
    L.set(106, GR - 1, 'K')
    # C · défi montant (111-137) : escalier, grand trou à plateformes
    L.stairs(111, 4)
    L.ground(115, 118, GR - 4)
    L.set(117, GR - 5, 'E')
    L.plat(121, 123, GR - 5); L.coins(121, 123, GR - 6)
    L.plat(126, 128, GR - 7); L.coins(126, 128, GR - 8)
    L.plat(131, 133, GR - 5); L.coins(131, 133, GR - 6)
    L.ground(136, 139, GR - 4)
    L.stairs(140, 3, up=False)
    L.set(129, GR - 11, 'H')                     # bloc caché n°3 (au-dessus du trou)
    # D · pause (143-150)
    L.ground(143, 169)
    L.row(145, GR - 4, '3P3')
    L.arc(143, 150, GR - 2, 2)
    # E · final : tuyaux + ennemis + grand escalier + drapeau
    L.pipe(151, 2); L.set(154, GR - 1, 'E'); L.pipe(156, 3)
    L.set(158, GR - 1, 'E')
    L.stairs(159, 6)
    L.set(166, GR - 1, 'G')
    return L


# ----------------------------------------------------------------------------------
# MONDE 2 · NUIT COSMIQUE  (176 x 40)  lave, glace, trampolines, volants
# ----------------------------------------------------------------------------------
def cosmo():
    L = Lvl(176)
    L.lava(0, L.w - 1)                           # lac de lave tout en bas
    L.ground(0, 20)
    L.set(3, GR - 1, 'S')
    L.arc(5, 10, GR - 2, 2)
    L.row(12, GR - 4, '3I3')
    L.set(17, GR - 1, 'E')
    # ponts de glace au-dessus de la lave
    L.plat(24, 30, GR, 'I')
    L.set(27, GR - 4, 'H')                       # caché n°1
    L.ground(34, 45)
    L.set(34, GR - 1, 'B')                       # trampoline -> route haute
    L.set(40, GR - 1, 'E')
    L.set(38, GR - 6, 'F')
    L.plat(48, 54, GR, 'I')
    L.ground(58, 70)
    L.row(62, GR - 4, '3P3')
    L.set(66, GR - 1, 'E')
    L.plat(74, 79, GR, 'I')
    L.set(76, GR - 6, 'F')
    L.ground(83, 110)
    L.set(88, GR - 1, 'E'); L.set(96, GR - 1, 'E')
    L.arc(99, 104, GR - 2, 2)
    # ROUTE HAUTE (32-100) : îles de glace + plateformes, par le trampoline de la col 34
    L.plat(30, 35, GR - 7)
    L.plat(38, 43, GR - 11); L.coins(38, 43, GR - 12)
    L.plat(46, 51, GR - 14)
    L.set(49, GR - 18, 'F')
    L.plat(54, 58, GR - 12, 'I')
    L.plat(61, 66, GR - 13); L.coins(61, 66, GR - 14)
    L.row(62, GR - 17, '3 3')
    L.plat(69, 73, GR - 12)
    L.set(71, GR - 16, 'H')                      # marche cachée -> SECRET
    L.plat(76, 81, GR - 11, 'I'); L.coins(76, 81, GR - 12)
    L.plat(84, 88, GR - 11); L.set(86, GR - 12, 'E')
    L.plat(91, 96, GR - 8)
    L.plat(99, 103, GR - 4)
    # SECRET : constellation de pistaches (rangées 18 -> 6)
    L.plat(73, 82, GR - 20); L.coins(73, 82, GR - 21)
    L.plat(79, 88, GR - 24); L.coins(79, 88, GR - 25)
    L.plat(85, 94, GR - 28); L.coins(85, 93, GR - 29); L.set(94, GR - 29, 'P')
    L.set(90, GR - 32, 'C'); L.set(91, GR - 32, 'C')
    L.set(106, GR - 1, 'K')
    # C · montée cosmique (112-150) : trampolines, lave, îles
    L.ground(114, 117, GR - 2)
    L.set(116, GR - 3, 'B')
    L.plat(118, 122, GR - 9); L.coins(118, 122, GR - 10)
    L.plat(125, 129, GR - 12); L.set(127, GR - 16, 'F')
    L.plat(132, 136, GR - 9)
    L.plat(139, 143, GR - 6)
    L.ground(146, 175)
    L.set(131, GR - 14, 'H')                     # caché n°3
    L.set(122, GR - 1, 'C')
    L.plat(120, 124, GR, 'I')                    # route basse de secours sur la lave
    L.plat(128, 132, GR, 'I')
    L.plat(136, 141, GR, 'I')
    L.set(138, GR - 1, 'E')
    # D · pause + portail
    L.row(149, GR - 4, '3P3')
    L.set(155, GR - 1, 'E'); L.set(160, GR - 6, 'F')
    L.stairs(162, 4, ch='I')
    L.ground(166, 175, GR - 4, 'I')
    L.set(170, GR - 5, 'G')
    return L


# ----------------------------------------------------------------------------------
# MONDE 3 · VAISSEAU PISTACHE  (176 x 40)  ponts, passerelles, raisins aliens
# ----------------------------------------------------------------------------------
def ship():
    L = Lvl(176)
    L.ground(0, 26)
    L.set(3, GR - 1, 'S')
    L.row(9, GR - 4, '232')
    L.set(13, GR - 4, '3')
    L.set(15, GR - 1, 'R'); L.set(22, GR - 1, 'R')
    L.set(19, GR - 4, 'H')
    L.ground(30, 60)                             # trou 27-29
    L.pipe(34, 2)
    L.set(39, GR - 1, 'R')
    L.set(44, GR - 1, 'B')                       # trampoline -> passerelles hautes
    L.stairs(52, 3)
    L.ground(55, 60, GR - 3)
    L.set(58, GR - 4, 'R')
    L.ground(64, 110)                            # trou 61-63
    L.row(68, GR - 4, '3P3')
    L.set(73, GR - 1, 'R'); L.set(80, GR - 1, 'R')
    L.pipe(84, 3)
    L.set(90, GR - 1, 'R')
    L.set(93, GR - 4, 'H')
    L.plat(96, 100, GR - 4); L.coins(96, 100, GR - 5)
    L.set(103, GR - 1, 'R')
    # ROUTE HAUTE : passerelles (traversables) dans la coque
    L.plat(40, 46, GR - 8)
    L.plat(48, 53, GR - 12); L.coins(48, 53, GR - 13)
    L.plat(56, 61, GR - 15); L.set(58, GR - 16, 'R')
    L.plat(64, 70, GR - 12)
    L.row(66, GR - 16, '3 3')
    L.plat(73, 78, GR - 15); L.coins(73, 78, GR - 16)
    L.plat(81, 86, GR - 12)
    L.set(83, GR - 16, 'H')                      # marche cachée -> SECRET
    L.plat(89, 94, GR - 14); L.set(91, GR - 15, 'R')
    L.plat(97, 102, GR - 11)
    L.plat(104, 107, GR - 7)
    # SECRET : soute aux pistaches (rangées 19 -> 7)
    L.plat(85, 94, GR - 20); L.coins(85, 94, GR - 21)
    L.plat(91, 100, GR - 24); L.coins(91, 100, GR - 25)
    L.plat(97, 106, GR - 28); L.coins(97, 105, GR - 29); L.set(106, GR - 29, 'P')
    L.set(109, GR - 1, 'K')
    # C · salle des machines (112-150)
    L.stairs(113, 4)
    L.ground(117, 120, GR - 4)
    L.set(119, GR - 5, 'R')
    L.set(121, GR - 5, 'B')
    L.ground(121, 121, GR - 4)
    L.plat(124, 128, GR - 10); L.coins(124, 128, GR - 11)
    L.plat(131, 135, GR - 8); L.set(133, GR - 9, 'R')
    L.plat(138, 142, GR - 6)
    L.set(130, GR - 14, 'H')
    L.ground(124, 142, GR)                       # route basse sous les passerelles
    L.pipe(127, 2); L.set(131, GR - 1, 'R'); L.pipe(135, 3); L.set(139, GR - 1, 'R')
    L.ground(145, 175)
    L.row(147, GR - 4, '3P3')
    L.set(153, GR - 1, 'R'); L.set(158, GR - 1, 'R')
    L.stairs(161, 5)
    L.ground(166, 175, GR - 5)
    L.set(170, GR - 6, 'G')
    return L


def main():
    out = {'park': park().rows(), 'cosmo': cosmo().rows(), 'ship': ship().rows()}
    js = ('// Généré par tools/levels/build_levels.py — ne pas éditer à la main.\n'
          '// Mondes « Super Mario World » : larges ET hauts, route haute / basse, secret, checkpoint.\n'
          'window.LEVEL_MAPS = ' + json.dumps(out, indent=1) + ';\n')
    p = os.path.join(ROOT, 'js', 'levels.js')
    open(p, 'w').write(js)
    for k, v in out.items():
        print(k, len(v[0]), 'x', len(v))


if __name__ == '__main__':
    main()
