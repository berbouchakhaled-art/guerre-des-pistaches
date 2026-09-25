"""Compare generated PNG pixels with tools/gfx/manifest.txt (sha256 of RGBA pixels).
python3 tools/gfx/check_manifest.py [--write]"""
import hashlib, os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ICONS = os.path.join(ROOT, 'assets/icons')
files = sorted(['assets/sousou-sprite.png']
               + ['assets/gfx/' + f for f in os.listdir(os.path.join(ROOT, 'assets/gfx')) if f.endswith('.png')]
               + (['assets/icons/' + f for f in os.listdir(ICONS) if f.endswith('.png')] if os.path.isdir(ICONS) else []))
def h(f):
    im = Image.open(os.path.join(ROOT, f)).convert('RGBA')
    return hashlib.sha256(im.tobytes()).hexdigest() + ' %dx%d' % im.size
man = os.path.join(HERE, 'manifest.txt')
if '--write' in sys.argv:
    open(man, 'w').write(''.join('%s %s\n' % (f, h(f)) for f in files)); print('manifest written'); sys.exit(0)
exp = {l.split()[0]: ' '.join(l.split()[1:]) for l in open(man) if l.strip()}
bad = 0
for f in files:
    got = h(f)
    if exp.get(f) != got: bad += 1; print('MISMATCH', f, got, 'expected', exp.get(f))
    else: print('ok', f)
print('mismatches:', bad)
