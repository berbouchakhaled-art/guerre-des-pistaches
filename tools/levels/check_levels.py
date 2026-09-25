"""Automated level checker (runs over the REAL level data used by the game).

  python3 tools/levels/check_levels.py            -> checks js/levels.js (new worlds)
  python3 tools/levels/check_levels.py --old FILE -> checks the rows inside an old index.html

Checks, for every world (parc, cosmique, vaisseau — the Histoire mode chains the same 3):
 1. CLEARANCE : every standable tile has >= 3 free tiles above it (player 36x52 px, tile 40 px)
    -> nobody ever has to crouch; also reports literal "crouch-only" passages (1 free tile).
 2. CEILINGS  : no solid ceiling (run of >= 4 solid tiles) within a NORMAL jump above a
    reachable standable tile (isolated ?-blocks / bricks are allowed, they are meant to be hit).
 3. REACHABILITY : frame-by-frame simulation of the game physics (same integration as
    resolvePlayer, hardest "Défi" jump), never crouching: start -> checkpoint -> goal must be
    reachable; secret area reachable once hidden ?-blocks are revealed.
Exit code 1 on any failure.
"""
import json, math, os, re, sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
T = 40
PW, PH = 36, 52
WALL = set('12356789BI')
ONEWAY = set('4')


def physics():
    src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    phys = {}
    for th in ('park', 'cosmo', 'ship'):
        m = re.search(r"theme: '%s',.*?gravity: ([\d.]+),.*?jumpV: (-[\d.]+)" % th, src, re.S)
        phys[th] = (float(m.group(1)), float(m.group(2)))
    diff = {}
    for m in re.finditer(r"(\w+): \{\s*id: '(\w+)'.*?jumpBonus: (-?[\d.]+).*?gravityMul: ([\d.]+)", src, re.S):
        diff[m.group(2)] = (float(m.group(3)), float(m.group(4)))
    return phys, diff


class Map:
    def __init__(self, rows, reveal=False, oneway=True):
        self.rows = rows
        self.R, self.C = len(rows), len(rows[0])
        self.reveal = reveal
        self.oneway = oneway

    def ch(self, c, r):
        if c < 0 or r < 0 or c >= self.C or r >= self.R:
            return '.'
        return self.rows[r][c]

    def wall(self, c, r):
        k = self.ch(c, r)
        if k == 'H':
            return self.reveal
        if k in ONEWAY and not self.oneway:
            return True
        return k in WALL

    def tile(self, c, r):   # anything you can stand on
        k = self.ch(c, r)
        return k in WALL or k in ONEWAY or (k == 'H' and self.reveal)

    def wall_px(self, x, y):
        return self.wall(math.floor(x / T), math.floor(y / T))

    def standable(self, c, r):
        return self.tile(c, r) and not self.tile(c, r - 1) and self.ch(c, r - 1) != 'X'

    def find(self, k):
        return [(c, r) for r in range(self.R) for c in range(self.C) if self.rows[r][c] == k]


def clearance(m):
    bad, crouch = [], []
    for r in range(m.R):
        for c in range(m.C):
            if not m.standable(c, r):
                continue
            free = 0
            for k in range(1, 4):
                kk = m.ch(c, r - k)
                if kk in WALL or kk in ONEWAY or kk == 'H':
                    break
                free += 1
            if free < 3:
                bad.append((c, r, free))
                if free == 1:
                    crouch.append((c, r))
    return bad, crouch


def simulate(m, x, y, vx0, dirn, spd, vy0, g, vmax_air, tramp_v):
    """Returns landing cell (c, r) or None. Integration identical to resolvePlayer()."""
    hw = PW / 2
    vx, vyy = vx0, vy0
    for f in range(400):
        # air control
        if dirn:
            vx += 0.52 * dirn
            if abs(vx) > spd:
                vx = spd * dirn
        else:
            vx *= 0.90
        vx = max(-vmax_air, min(vmax_air, vx))
        x += vx
        top = y - PH
        for sy in (top + 4, y - PH / 2, y - 4):
            if vx > 0 and m.wall_px(x + hw, sy):
                x = math.floor((x + hw) / T) * T - hw - 0.01; vx = 0
            if vx < 0 and m.wall_px(x - hw, sy):
                x = (math.floor((x - hw) / T) + 1) * T + hw + 0.01; vx = 0
        prev = y
        vyy = min(14, vyy + g)
        y += vyy
        xs = (x - hw + 4, x, x + hw - 4)
        if vyy >= 0:
            for sx in xs:
                c, r = math.floor(sx / T), math.floor(y / T)
                k = m.ch(c, r)
                land = m.wall(c, r) or (k in ONEWAY and prev <= r * T + 1)
                if land:
                    if k == 'B':
                        y = r * T - 0.01; vyy = tramp_v
                        break
                    return (c, r, x)
        else:
            for sx in xs:
                if m.wall_px(sx, y - PH):
                    r = math.floor((y - PH) / T)
                    y = (r + 1) * T + PH + 0.01
                    vyy = 0.5
                    break
        c0 = math.floor(x / T)
        if m.ch(c0, math.floor((y - 4) / T)) == 'X' or m.ch(c0, math.floor((y - PH / 2) / T)) == 'X':
            return None
        if y > m.R * T + 80:
            return None
        if x < hw:
            x = hw
        if x > m.C * T - hw:
            x = m.C * T - hw
    return None


def reach(m, theme, phys, diff, level='hard'):
    grav, jv = phys[theme]
    jb, gm = diff[level]
    g = grav * gm
    jump = jv + jb
    vmax_air = 5.9 if theme == 'cosmo' else 5.6
    tramp = -18 if theme == 'cosmo' else -16
    start = m.find('S')[0]
    s0 = (start[0], start[1] + 1)
    seen = {s0}
    q = deque([s0])
    edges = 0
    while q:
        c, r = q.popleft()
        nxt = []
        # marcher (debout, sans jamais s'accroupir : 2 tuiles libres au-dessus)
        for d in (-1, 1):
            cc = c + d
            if m.standable(cc, r) and not m.wall(cc, r - 1) and not m.wall(cc, r - 2):
                nxt.append((cc, r))
        feet = r * T - 0.01
        if m.ch(c, r) == 'B':
            launches = [(tramp, c * T + T / 2)]
        else:
            launches = [(jump, c * T + T / 2)]
        for vy0, x0 in launches:
            for dirn, spd in ((0, 0), (1, 2), (1, 3.5), (1, 5.6), (-1, 2), (-1, 3.5), (-1, 5.6)):
                res = simulate(m, x0, feet, dirn * spd, dirn, spd, vy0, g, vmax_air, tramp)
                if res:
                    nxt.append(res[:2])
        # se laisser tomber d'un bord
        for d in (-1, 1):
            if not m.standable(c + d, r) and not m.wall(c + d, r - 1):
                for spd in (1.5, 3.5, 5.6):
                    res = simulate(m, c * T + T / 2 + d * 16, feet, d * spd, d, spd, 0, g, vmax_air, tramp)
                    if res:
                        nxt.append(res[:2])
        for n in nxt:
            edges += 1
            if n not in seen and m.standable(*n):
                seen.add(n)
                q.append(n)
    return seen


def ceilings(m, reachable, phys, diff, theme):
    grav, jv = phys[theme]
    jb, gm = diff['normal']
    hmax = (jv + jb) ** 2 / (2 * grav * gm) + PH
    rows_up = int(math.ceil(hmax / T))
    bad = set()
    for (c, r) in reachable:
        for k in range(4, rows_up + 1):
            if m.wall(c, r - k) and m.ch(c, r - k) not in 'H':
                run = 1
                a = c - 1
                while m.wall(a, r - k): run += 1; a -= 1
                a = c + 1
                while m.wall(a, r - k): run += 1; a += 1
                if run >= 4:
                    bad.add((c, r - k, run))
                break
    return sorted(bad)


def check(name, theme, rows, phys, diff, new=True):
    ok = True
    m = Map(rows)
    print('== %s (%s) %d x %d tiles = %d x %d px' % (name, theme, m.C, m.R, m.C * T, m.R * T))
    bad, crouch = clearance(m)
    print('  clearance < 3 tiles above a standable tile : %d cell(s)%s' % (len(bad), (' e.g. ' + str(bad[:8])) if bad else ''))
    print('  crouch-only passages (1 free tile)         : %d%s' % (len(crouch), (' e.g. ' + str(crouch[:8])) if crouch else ''))
    if bad:
        ok = False
    if not new:
        return ok
    R = reach(m, theme, phys, diff, 'hard')
    Rn = reach(Map(rows, reveal=True), theme, phys, diff, 'hard')
    ceil = ceilings(m, R, phys, diff, theme)
    print('  solid ceilings within a normal jump        : %d%s' % (len(ceil), (' ' + str(ceil[:6])) if ceil else ''))
    if ceil:
        ok = False
    def under(k):
        c, r = m.find(k)[0]
        return (c, r + 1)
    for k, label in (('K', 'checkpoint'), ('G', 'goal')):
        cell = under(k)
        hit = cell in R
        print('  start -> %-10s reachable (Défi physics, no crouch, secrets hidden): %s' % (label, 'YES' if hit else 'NO'))
        ok &= hit
    coins = m.find('C')
    def coin_ok(S, c, r):   # standing below it, or within a jump arc (pits)
        return any((c + dc, rr) in S for dc in range(-4, 5) for rr in range(r + 1, r + 6))
    cz = sum(coin_ok(R, c, r) for c, r in coins)
    czs = sum(coin_ok(Rn, c, r) for c, r in coins)
    hid = m.find('H')
    top = min(r for c, r in m.find('4') + m.find('I')) if (m.find('4') or m.find('I')) else 0
    sec = [cell for cell in Rn if cell[1] <= top + 1]
    print('  hidden ?-blocks: %d · pistachios reachable: %d/%d (all %d/%d once hidden blocks are found)'
          % (len(hid), cz, len(coins), czs, len(coins)))
    print('  secret sky area (row %d, %d tiles above ground) reachable via hidden blocks: %s'
          % (top, 35 - top, 'YES' if sec else 'NO'))
    ok &= bool(sec)
    print('  reachable standable cells: %d (Défi) / %d (with secrets)' % (len(R), len(Rn)))
    return ok


def old_levels(path):
    src = open(path, encoding='utf-8').read()
    out = []
    for m in re.finditer(r"theme: '(\w+)'.*?rows: \[(.*?)\n      \]", src, re.S):
        rows = re.findall(r"^\s*'([^']*)',\s*$", m.group(2), re.M)
        out.append((m.group(1), rows))
    return out


def main():
    phys, diff = physics()
    names = {'park': 'Monde 1 · Parc', 'cosmo': 'Monde 2 · Cosmique', 'ship': 'Monde 3 · Vaisseau'}
    if '--old' in sys.argv:
        allok = True
        for th, rows in old_levels(sys.argv[sys.argv.index('--old') + 1]):
            allok &= check(names[th] + ' (ANCIEN)', th, rows, phys, diff, new=False)
        print('RESULT:', 'OK' if allok else 'FAIL')
        sys.exit(0 if allok else 1)
    src = open(os.path.join(ROOT, 'js', 'levels.js'), encoding='utf-8').read()
    maps = json.loads(src[src.index('=') + 1:src.rindex(';')])
    allok = True
    for th in ('park', 'cosmo', 'ship'):
        allok &= check(names[th], th, maps[th], phys, diff)
    print('Histoire = enchaînement des 3 mondes ci-dessus (mêmes cartes).')
    print('RESULT:', 'OK' if allok else 'FAIL')
    sys.exit(0 if allok else 1)


if __name__ == '__main__':
    main()
